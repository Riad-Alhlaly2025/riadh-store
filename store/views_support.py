from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import LiveChatSession, LiveChatMessage, SupportTicket, SupportTicketReply, FAQCategory, FAQ, EnhancedReview
from .decorators import manager_required

def is_manager(user):
    """Check if user is a manager"""
    return user.userprofile.role == 'manager'

def is_support_agent(user):
    """Check if user is a support agent"""
    return user.userprofile.role in ['manager', 'support_agent']

# Live Chat Views
@login_required
def chat_list(request: HttpRequest) -> HttpResponse:
    """List chat sessions for the user"""
    # Get user's chat sessions
    chat_sessions = LiveChatSession.objects.filter(
        Q(customer=request.user) | Q(support_agent=request.user)
    ).order_by('-updated_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        chat_sessions = chat_sessions.filter(status=status_filter)
    
    paginator = Paginator(chat_sessions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
    }
    return render(request, 'store/chat_list.html', context)

@login_required
def chat_detail(request: HttpRequest, chat_id: int) -> HttpResponse:
    """View chat details and messages"""
    chat_session = get_object_or_404(LiveChatSession, id=chat_id)
    
    # Check if user has access to this chat
    if request.user != chat_session.customer and request.user != chat_session.support_agent:
        messages.error(request, 'ليس لديك صلاحية لعرض هذه الدردشة')
        return redirect('chat_list')
    
    # Get messages
    messages_list = LiveChatMessage.objects.filter(chat_session=chat_session).order_by('timestamp')
    
    # Mark messages as read if user is the recipient
    if request.user == chat_session.support_agent:
        LiveChatMessage.objects.filter(
            chat_session=chat_session,
            sender=chat_session.customer,
            is_read=False
        ).update(is_read=True)
    elif request.user == chat_session.customer:
        LiveChatMessage.objects.filter(
            chat_session=chat_session,
            sender=chat_session.support_agent,
            is_read=False
        ).update(is_read=True)
    
    # Handle message submission
    if request.method == 'POST' and request.user.is_authenticated:
        message_content = request.POST.get('message', '').strip()
        if message_content:
            LiveChatMessage.objects.create(
                chat_session=chat_session,
                sender=request.user,
                message=message_content
            )
            # Update chat session timestamp
            chat_session.updated_at = timezone.now()
            chat_session.save()
            return redirect('chat_detail', chat_id=chat_id)
        else:
            messages.error(request, 'يرجى كتابة رسالة')
    
    context = {
        'chat_session': chat_session,
        'messages_list': messages_list,
    }
    return render(request, 'store/chat_detail.html', context)

@login_required
def start_chat(request: HttpRequest) -> HttpResponse:
    """Start a new chat session"""
    if request.method == 'POST':
        topic = request.POST.get('topic', '').strip()
        if topic:
            chat_session = LiveChatSession.objects.create(
                customer=request.user,
                topic=topic,
                status='pending'
            )
            messages.success(request, 'تم بدء جلسة الدردشة بنجاح')
            return redirect('chat_detail', chat_id=chat_session.id)
        else:
            messages.error(request, 'يرجى تحديد موضوع للدردشة')
    
    return render(request, 'store/start_chat.html')

@user_passes_test(is_support_agent)
def agent_chat_list(request: HttpRequest) -> HttpResponse:
    """List chat sessions for support agents"""
    # Get pending and active chat sessions
    chat_sessions = LiveChatSession.objects.filter(
        Q(status='pending') | Q(status='active') | Q(support_agent=request.user)
    ).order_by('-updated_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        chat_sessions = chat_sessions.filter(status=status_filter)
    
    paginator = Paginator(chat_sessions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
    }
    return render(request, 'store/agent_chat_list.html', context)

@user_passes_test(is_support_agent)
def assign_chat(request: HttpRequest, chat_id: int) -> HttpResponse:
    """Assign a chat session to a support agent"""
    chat_session = get_object_or_404(LiveChatSession, id=chat_id, status='pending')
    
    if request.method == 'POST':
        chat_session.support_agent = request.user
        chat_session.status = 'active'
        chat_session.save()
        messages.success(request, 'تم تعيين جلسة الدردشة لك بنجاح')
        return redirect('chat_detail', chat_id=chat_id)
    
    context = {
        'chat_session': chat_session,
    }
    return render(request, 'store/assign_chat.html', context)

@user_passes_test(is_support_agent)
def close_chat(request: HttpRequest, chat_id: int) -> HttpResponse:
    """Close a chat session"""
    chat_session = get_object_or_404(LiveChatSession, id=chat_id)
    
    if request.method == 'POST':
        chat_session.status = 'closed'
        chat_session.closed_at = timezone.now()
        chat_session.save()
        messages.success(request, 'تم إغلاق جلسة الدردشة بنجاح')
        return redirect('agent_chat_list')
    
    context = {
        'chat_session': chat_session,
    }
    return render(request, 'store/close_chat.html', context)

# Support Ticket Views
@login_required
def ticket_list(request: HttpRequest) -> HttpResponse:
    """List support tickets for the user"""
    tickets = SupportTicket.objects.filter(customer=request.user).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    # Filter by priority
    priority_filter = request.GET.get('priority')
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    }
    return render(request, 'store/ticket_list.html', context)

@login_required
def ticket_detail(request: HttpRequest, ticket_id: int) -> HttpResponse:
    """View ticket details and replies"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id, customer=request.user)
    
    # Get replies
    replies = SupportTicketReply.objects.filter(ticket=ticket).order_by('created_at')
    
    # Handle reply submission
    if request.method == 'POST' and request.user.is_authenticated:
        message_content = request.POST.get('message', '').strip()
        if message_content:
            SupportTicketReply.objects.create(
                ticket=ticket,
                author=request.user,
                message=message_content
            )
            # Update ticket status to reopened if it was closed
            if ticket.status == 'closed':
                ticket.status = 'reopened'
                ticket.save()
            messages.success(request, 'تم إرسال ردك بنجاح')
            return redirect('ticket_detail', ticket_id=ticket_id)
        else:
            messages.error(request, 'يرجى كتابة رد')
    
    context = {
        'ticket': ticket,
        'replies': replies,
    }
    return render(request, 'store/ticket_detail.html', context)

@login_required
def create_ticket(request: HttpRequest) -> HttpResponse:
    """Create a new support ticket"""
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', 'other')
        priority = request.POST.get('priority', 'medium')
        
        if subject and description:
            ticket = SupportTicket.objects.create(
                customer=request.user,
                subject=subject,
                description=description,
                category=category,
                priority=priority
            )
            messages.success(request, 'تم إنشاء التذكرة بنجاح')
            return redirect('ticket_detail', ticket_id=ticket.id)
        else:
            messages.error(request, 'يرجى ملء الحقول المطلوبة')
    
    return render(request, 'store/create_ticket.html')

@user_passes_test(is_support_agent)
def agent_ticket_list(request: HttpRequest) -> HttpResponse:
    """List support tickets for support agents"""
    tickets = SupportTicket.objects.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    # Filter by priority
    priority_filter = request.GET.get('priority')
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    
    # Filter by category
    category_filter = request.GET.get('category')
    if category_filter:
        tickets = tickets.filter(category=category_filter)
    
    # Filter by assigned agent
    agent_filter = request.GET.get('agent')
    if agent_filter:
        if agent_filter == 'unassigned':
            tickets = tickets.filter(assigned_agent__isnull=True)
        else:
            tickets = tickets.filter(assigned_agent__id=agent_filter)
    
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get agents for filter dropdown
    agents = User.objects.filter(userprofile__role__in=['manager', 'support_agent'])
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'agent_filter': agent_filter,
        'agents': agents,
    }
    return render(request, 'store/agent_ticket_list.html', context)

@user_passes_test(is_support_agent)
def assign_ticket(request: HttpRequest, ticket_id: int) -> HttpResponse:
    """Assign a ticket to a support agent"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    if request.method == 'POST':
        agent_id = request.POST.get('agent')
        if agent_id:
            agent = get_object_or_404(User, id=agent_id)
            ticket.assigned_agent = agent
            if ticket.status == 'open':
                ticket.status = 'in_progress'
            ticket.save()
            messages.success(request, 'تم تعيين التذكرة بنجاح')
            return redirect('agent_ticket_list')
        else:
            messages.error(request, 'يرجى اختيار وكيل دعم')
    
    # Get agents for assignment
    agents = User.objects.filter(userprofile__role__in=['manager', 'support_agent'])
    
    context = {
        'ticket': ticket,
        'agents': agents,
    }
    return render(request, 'store/assign_ticket.html', context)

@user_passes_test(is_support_agent)
def resolve_ticket(request: HttpRequest, ticket_id: int) -> HttpResponse:
    """Resolve a ticket"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    if request.method == 'POST':
        resolution_notes = request.POST.get('resolution_notes', '').strip()
        ticket.status = 'resolved'
        ticket.resolved_at = timezone.now()
        ticket.resolution_notes = resolution_notes
        ticket.save()
        messages.success(request, 'تم حل التذكرة بنجاح')
        return redirect('agent_ticket_list')
    
    context = {
        'ticket': ticket,
    }
    return render(request, 'store/resolve_ticket.html', context)

# FAQ Views
def faq_list(request: HttpRequest) -> HttpResponse:
    """List FAQ categories and questions"""
    # Get active FAQ categories
    categories = FAQCategory.objects.filter(is_active=True).order_by('order')
    
    # Get active FAQs
    faqs = FAQ.objects.filter(is_active=True).order_by('category__order', 'order')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        faqs = faqs.filter(
            Q(question__icontains=search_query) | 
            Q(answer__icontains=search_query)
        )
    
    # Filter by category
    category_filter = request.GET.get('category')
    if category_filter:
        faqs = faqs.filter(category__id=category_filter)
    
    paginator = Paginator(faqs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'categories': categories,
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
    }
    return render(request, 'store/faq_list.html', context)

def faq_detail(request: HttpRequest, faq_id: int) -> HttpResponse:
    """View FAQ details"""
    faq = get_object_or_404(FAQ, id=faq_id, is_active=True)
    
    # Increment view count
    faq.views += 1
    faq.save(update_fields=['views'])
    
    context = {
        'faq': faq,
    }
    return render(request, 'store/faq_detail.html', context)

@manager_required
def faq_category_list(request: HttpRequest) -> HttpResponse:
    """List FAQ categories for managers"""
    categories = FAQCategory.objects.all().order_by('order')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        categories = categories.filter(name__icontains=search_query)
    
    paginator = Paginator(categories, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'store/faq_category_list.html', context)

@manager_required
def faq_category_create(request: HttpRequest) -> HttpResponse:
    """Create a new FAQ category"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active', 'on') == 'on'
        
        if name:
            FAQCategory.objects.create(
                name=name,
                description=description,
                order=order,
                is_active=is_active
            )
            messages.success(request, 'تم إنشاء فئة الأسئلة الشائعة بنجاح')
            return redirect('faq_category_list')
        else:
            messages.error(request, 'يرجى ملء الحقول المطلوبة')
    
    return render(request, 'store/faq_category_form.html', {'action': 'create'})

@manager_required
def faq_category_edit(request: HttpRequest, category_id: int) -> HttpResponse:
    """Edit an FAQ category"""
    category = get_object_or_404(FAQCategory, id=category_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active', 'on') == 'on'
        
        if name:
            category.name = name
            category.description = description
            category.order = order
            category.is_active = is_active
            category.save()
            messages.success(request, 'تم تحديث فئة الأسئلة الشائعة بنجاح')
            return redirect('faq_category_list')
        else:
            messages.error(request, 'يرجى ملء الحقول المطلوبة')
    
    context = {
        'category': category,
        'action': 'edit',
    }
    return render(request, 'store/faq_category_form.html', context)

@manager_required
def faq_category_delete(request: HttpRequest, category_id: int) -> HttpResponse:
    """Delete an FAQ category"""
    category = get_object_or_404(FAQCategory, id=category_id)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'تم حذف فئة الأسئلة الشائعة بنجاح')
        return redirect('faq_category_list')
    
    context = {
        'category': category,
    }
    return render(request, 'store/faq_category_confirm_delete.html', context)

@manager_required
def faq_list_manager(request: HttpRequest) -> HttpResponse:
    """List FAQs for managers"""
    faqs = FAQ.objects.all().order_by('category__order', 'order')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        faqs = faqs.filter(
            Q(question__icontains=search_query) | 
            Q(answer__icontains=search_query)
        )
    
    # Filter by category
    category_filter = request.GET.get('category')
    if category_filter:
        faqs = faqs.filter(category__id=category_filter)
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        if status_filter == 'active':
            faqs = faqs.filter(is_active=True)
        elif status_filter == 'inactive':
            faqs = faqs.filter(is_active=False)
    
    paginator = Paginator(faqs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter dropdown
    categories = FAQCategory.objects.all()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'status_filter': status_filter,
        'categories': categories,
    }
    return render(request, 'store/faq_list_manager.html', context)

@manager_required
def faq_create(request: HttpRequest) -> HttpResponse:
    """Create a new FAQ"""
    if request.method == 'POST':
        category_id = request.POST.get('category')
        question = request.POST.get('question', '').strip()
        answer = request.POST.get('answer', '').strip()
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active', 'on') == 'on'
        
        if category_id and question and answer:
            category = get_object_or_404(FAQCategory, id=category_id)
            FAQ.objects.create(
                category=category,
                question=question,
                answer=answer,
                order=order,
                is_active=is_active
            )
            messages.success(request, 'تم إنشاء السؤال الشائع بنجاح')
            return redirect('faq_list_manager')
        else:
            messages.error(request, 'يرجى ملء الحقول المطلوبة')
    
    # Get categories for dropdown
    categories = FAQCategory.objects.all()
    
    context = {
        'categories': categories,
        'action': 'create',
    }
    return render(request, 'store/faq_form.html', context)

@manager_required
def faq_edit(request: HttpRequest, faq_id: int) -> HttpResponse:
    """Edit an FAQ"""
    faq = get_object_or_404(FAQ, id=faq_id)
    
    if request.method == 'POST':
        category_id = request.POST.get('category')
        question = request.POST.get('question', '').strip()
        answer = request.POST.get('answer', '').strip()
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active', 'on') == 'on'
        
        if category_id and question and answer:
            category = get_object_or_404(FAQCategory, id=category_id)
            faq.category = category
            faq.question = question
            faq.answer = answer
            faq.order = order
            faq.is_active = is_active
            faq.save()
            messages.success(request, 'تم تحديث السؤال الشائع بنجاح')
            return redirect('faq_list_manager')
        else:
            messages.error(request, 'يرجى ملء الحقول المطلوبة')
    
    # Get categories for dropdown
    categories = FAQCategory.objects.all()
    
    context = {
        'faq': faq,
        'categories': categories,
        'action': 'edit',
    }
    return render(request, 'store/faq_form.html', context)

@manager_required
def faq_delete(request: HttpRequest, faq_id: int) -> HttpResponse:
    """Delete an FAQ"""
    faq = get_object_or_404(FAQ, id=faq_id)
    
    if request.method == 'POST':
        faq.delete()
        messages.success(request, 'تم حذف السؤال الشائع بنجاح')
        return redirect('faq_list_manager')
    
    context = {
        'faq': faq,
    }
    return render(request, 'store/faq_confirm_delete.html', context)

# Enhanced Review Views
def product_reviews(request: HttpRequest, product_id: int) -> HttpResponse:
    """List enhanced reviews for a product"""
    from .models import Product
    product = get_object_or_404(Product, id=product_id)
    
    # Get approved reviews
    reviews = EnhancedReview.objects.filter(
        product=product,
        is_verified_purchase=True
    ).order_by('-created_at')
    
    # Filter by rating
    rating_filter = request.GET.get('rating')
    if rating_filter:
        reviews = reviews.filter(rating=rating_filter)
    
    # Filter by featured
    featured_filter = request.GET.get('featured')
    if featured_filter:
        reviews = reviews.filter(is_featured=True)
    
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'product': product,
        'page_obj': page_obj,
        'rating_filter': rating_filter,
        'featured_filter': featured_filter,
    }
    return render(request, 'store/product_reviews.html', context)

@login_required
def add_review(request: HttpRequest, product_id: int) -> HttpResponse:
    """Add an enhanced review for a product"""
    from .models import Product
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user has purchased the product
    from .models import OrderItem
    is_verified = OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__status='delivered'
    ).exists()
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        title = request.POST.get('title', '').strip()
        comment = request.POST.get('comment', '').strip()
        pros = request.POST.get('pros', '').strip()
        cons = request.POST.get('cons', '').strip()
        
        if rating and title and comment:
            # Create or update review
            review, created = EnhancedReview.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={
                    'rating': rating,
                    'title': title,
                    'comment': comment,
                    'pros': pros,
                    'cons': cons,
                    'is_verified_purchase': is_verified
                }
            )
            
            if not created:
                # Update existing review
                review.rating = rating
                review.title = title
                review.comment = comment
                review.pros = pros
                review.cons = cons
                review.is_verified_purchase = is_verified
                review.save()
                messages.success(request, 'تم تحديث تقييمك بنجاح')
            else:
                messages.success(request, 'تم إضافة تقييمك بنجاح')
            
            return redirect('product_reviews', product_id=product_id)
        else:
            messages.error(request, 'يرجى ملء الحقول المطلوبة')
    
    context = {
        'product': product,
        'is_verified': is_verified,
    }
    return render(request, 'store/add_enhanced_review.html', context)

@login_required
def review_helpfulness(request: HttpRequest, review_id: int, action: str) -> HttpResponse:
    """Mark a review as helpful or not helpful"""
    review = get_object_or_404(EnhancedReview, id=review_id)
    
    if action == 'helpful':
        review.helpful_count += 1
        review.save()
        messages.success(request, 'شكرًا على ملاحظاتك')
    elif action == 'not_helpful':
        review.not_helpful_count += 1
        review.save()
        messages.success(request, 'شكرًا على ملاحظاتك')
    
    return redirect('product_reviews', product_id=review.product.id)

@manager_required
def review_list_manager(request: HttpRequest) -> HttpResponse:
    """List all reviews for managers"""
    reviews = EnhancedReview.objects.all().order_by('-created_at')
    
    # Filter by product
    product_filter = request.GET.get('product')
    if product_filter:
        reviews = reviews.filter(product__name__icontains=product_filter)
    
    # Filter by rating
    rating_filter = request.GET.get('rating')
    if rating_filter:
        reviews = reviews.filter(rating=rating_filter)
    
    # Filter by featured status
    featured_filter = request.GET.get('featured')
    if featured_filter:
        if featured_filter == 'yes':
            reviews = reviews.filter(is_featured=True)
        elif featured_filter == 'no':
            reviews = reviews.filter(is_featured=False)
    
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'product_filter': product_filter,
        'rating_filter': rating_filter,
        'featured_filter': featured_filter,
    }
    return render(request, 'store/review_list_manager.html', context)

@manager_required
def toggle_featured_review(request: HttpRequest, review_id: int) -> HttpResponse:
    """Toggle featured status of a review"""
    review = get_object_or_404(EnhancedReview, id=review_id)
    
    review.is_featured = not review.is_featured
    review.save()
    
    if review.is_featured:
        messages.success(request, 'تم تمييز التقييم كمميز')
    else:
        messages.success(request, 'تم إلغاء تمييز التقييم')
    
    return redirect('review_list_manager')