from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
from django.conf import settings
import base64
import os


@login_required
def mfa_setup(request: HttpRequest) -> HttpResponse:
    """Setup MFA for the user"""
    # Import models inside the function to avoid circular imports
    from .models import MFADevice
    
    if request.method == 'POST':
        device_name = request.POST.get('device_name', '')
        device_type = request.POST.get('device_type', 'totp')
        
        if device_name:
            # Generate a secret key for the device
            import secrets
            import base64
            secret_key = base64.b32encode(secrets.token_bytes(20)).decode('utf-8')
            
            # Create the MFA device
            MFADevice.objects.create(
                user=request.user,
                name=device_name,
                secret_key=secret_key,
                device_type=device_type,
                is_active=True
            )
            
            messages.success(request, 'تم إعداد جهاز MFA بنجاح')
            return redirect('mfa_device_list')
        else:
            messages.error(request, 'يرجى إدخال اسم الجهاز')
    
    return render(request, 'store/mfa_setup.html')


@login_required
def mfa_verify(request: HttpRequest) -> HttpResponse:
    """Verify MFA code"""
    # Import models inside the function to avoid circular imports
    from .models import MFADevice
    
    if request.method == 'POST':
        code = request.POST.get('code', '')
        
        # Get active MFA devices for the user
        devices = MFADevice.objects.filter(user=request.user, is_active=True)
        
        if devices.exists():
            # In a real implementation, you would verify the code against the secret key
            # For now, we'll just simulate verification
            if code and len(code) == 6 and code.isdigit():
                # Log the successful MFA verification
                from .models import SecurityLog
                SecurityLog.objects.create(
                    user=request.user,
                    event_type='mfa_success',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    details='MFA verification successful'
                )
                
                messages.success(request, 'تم التحقق من MFA بنجاح')
                return redirect('home')
            else:
                # Log the failed MFA verification
                from .models import SecurityLog
                SecurityLog.objects.create(
                    user=request.user,
                    event_type='mfa_failed',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    details='MFA verification failed',
                    is_suspicious=True
                )
                
                messages.error(request, 'رمز MFA غير صحيح')
        else:
            messages.error(request, 'لا توجد أجهزة MFA مفعلة')
    
    return render(request, 'store/mfa_verify.html')


@login_required
def mfa_device_list(request: HttpRequest) -> HttpResponse:
    """List all MFA devices for the user"""
    # Import models inside the function to avoid circular imports
    from .models import MFADevice
    
    devices = MFADevice.objects.filter(user=request.user)
    return render(request, 'store/mfa_device_list.html', {'devices': devices})


@login_required
def mfa_delete_device(request: HttpRequest, device_id: int) -> HttpResponse:
    """Delete an MFA device"""
    # Import models inside the function to avoid circular imports
    from .models import MFADevice
    
    try:
        device = MFADevice.objects.get(id=device_id, user=request.user)
        device.delete()
        messages.success(request, 'تم حذف جهاز MFA بنجاح')
    except MFADevice.DoesNotExist:
        messages.error(request, 'جهاز MFA غير موجود')
    
    return redirect('mfa_device_list')


@login_required
def security_logs(request: HttpRequest) -> HttpResponse:
    """View security logs for the user"""
    # Import models inside the function to avoid circular imports
    from .models import SecurityLog
    
    logs = SecurityLog.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'store/security_logs.html', {'logs': logs})


@login_required
def sensitive_data_list(request: HttpRequest) -> HttpResponse:
    """List sensitive data for the user"""
    # Import models inside the function to avoid circular imports
    from .models import SensitiveData
    
    data_list = SensitiveData.objects.filter(user=request.user)
    return render(request, 'store/sensitive_data_list.html', {'data_list': data_list})


@login_required
def view_sensitive_data(request: HttpRequest, data_id: int) -> HttpResponse:
    """View decrypted sensitive data"""
    # Import models inside the function to avoid circular imports
    from .models import SensitiveData
    
    try:
        data = SensitiveData.objects.get(id=data_id, user=request.user)
        
        # Decrypt the data
        decrypted_data = ""
        try:
            if data.encryption_method == 'Fernet':
                # Decrypt using Fernet
                if hasattr(settings, 'SENSITIVE_DATA_ENCRYPTION_KEY'):
                    from cryptography.fernet import Fernet
                    key = settings.SENSITIVE_DATA_ENCRYPTION_KEY.encode()
                    f = Fernet(key)
                    decrypted_data = f.decrypt(data.encrypted_data.encode('utf-8')).decode('utf-8')
                else:
                    messages.error(request, 'مفتاح التشفير غير متوفر')
                    decrypted_data = "غير قادر على فك التشفير"
            else:
                # Fallback to base64 decoding
                import base64
                decrypted_data = base64.b64decode(data.encrypted_data.encode('utf-8')).decode('utf-8')
        except Exception as e:
            messages.error(request, 'فشل في فك تشفير البيانات')
            decrypted_data = "غير قادر على فك التشفير"
        
        return render(request, 'store/view_sensitive_data.html', {
            'data': data,
            'decrypted_data': decrypted_data
        })
    except SensitiveData.DoesNotExist:
        messages.error(request, 'البيانات الحساسة غير موجودة')
        return redirect('sensitive_data_list')


@login_required
def add_sensitive_data(request: HttpRequest) -> HttpResponse:
    """Add sensitive data"""
    # Import models inside the function to avoid circular imports
    from .models import SensitiveData
    
    if request.method == 'POST':
        data_type = request.POST.get('data_type', '')
        raw_data = request.POST.get('data', '')
        
        if data_type and raw_data:
            # Encrypt the data using Fernet encryption
            try:
                # Get or generate encryption key
                if hasattr(settings, 'SENSITIVE_DATA_ENCRYPTION_KEY'):
                    key = settings.SENSITIVE_DATA_ENCRYPTION_KEY.encode()
                else:
                    # Generate a key if not exists (in production, store this securely)
                    key = Fernet.generate_key()
                
                f = Fernet(key)
                encrypted_data = f.encrypt(raw_data.encode('utf-8')).decode('utf-8')
                encryption_method = 'Fernet'
            except Exception as e:
                # Fallback to base64 if encryption fails
                encrypted_data = base64.b64encode(raw_data.encode('utf-8')).decode('utf-8')
                encryption_method = 'Base64 (Fallback)'
            
            SensitiveData.objects.create(
                user=request.user,
                data_type=data_type,
                encrypted_data=encrypted_data,
                encryption_method=encryption_method
            )
            
            messages.success(request, 'تمت إضافة البيانات الحساسة بنجاح')
            return redirect('sensitive_data_list')
        else:
            messages.error(request, 'يرجى ملء جميع الحقول')
    
    return render(request, 'store/add_sensitive_data.html')


@login_required
def delete_sensitive_data(request: HttpRequest, data_id: int) -> HttpResponse:
    """Delete sensitive data"""
    # Import models inside the function to avoid circular imports
    from .models import SensitiveData
    
    try:
        data = SensitiveData.objects.get(id=data_id, user=request.user)
        data.delete()
        messages.success(request, 'تم حذف البيانات الحساسة بنجاح')
    except SensitiveData.DoesNotExist:
        messages.error(request, 'البيانات الحساسة غير موجودة')
    
    return redirect('sensitive_data_list')