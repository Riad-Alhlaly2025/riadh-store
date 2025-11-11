from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify
from .models import Page, Article, LandingPage, Comment
from .decorators import manager_required

def is_manager(user):
    """Check if user is a manager"""
    return user.userprofile.role == 'manager'

# Page Views
def page_detail(request: HttpRequest, slug: str) -> HttpResponse:
    """Display a page"""
    page = get_object_or_404(Page, slug=slug, status='published')
    # Get approved comments for this page
    comments = Comment.objects.filter(page=page, status='approved').order_by('-created_at')
    
    # Handle comment submission
    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content', '').strip()
        if content:
            Comment.objects.create(
                content=content,
                author=request.user,
                page=page,
                status='pending'
            )
            messages.success(request, 'تم إرسال تعليقك بنجاح وسينشر بعد المراجعة')
        else:
            messages.error(request, 'يرجى كتابة تعليق')
    
    context = {
        'page': page,
        'comments': comments,
    }
    return render(request, 'store/page_detail.html', context)

@manager_required
def page_list(request: HttpRequest) -> HttpResponse:
    """List all pages for managers"""
    pages = Page.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        pages = pages.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        pages = pages.filter(status=status_filter)
    
    paginator = Paginator(pages, 10)  # Show 10 pages per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'store/page_list.html', context)

@manager_required
def page_create(request: HttpRequest) -> HttpResponse:
    """Create a new page"""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        excerpt = request.POST.get('excerpt', '').strip()
        status = request.POST.get('status', 'draft')
        seo_title = request.POST.get('seo_title', '').strip()
        seo_description = request.POST.get('seo_description', '').strip()
        seo_keywords = request.POST.get('seo_keywords', '').strip()
        
        if title and content:
            # Generate slug from title
            slug = slugify(title)
            # Ensure slug is unique
            original_slug = slug
            counter = 1
            while Page.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            page = Page.objects.create(
                title=title,
                slug=slug,
                content=content,
                excerpt=excerpt,
                status=status,
                seo_title=seo_title,
                seo_description=seo_description,
                seo_keywords=seo_keywords,
            )
            
            if status == 'published':
                page.published_at = timezone.now()
                page.save()
            
            messages.success(request, 'تم إنشاء الصفحة بنجاح')
            return redirect('page_detail', slug=page.slug)
        else:
            messages.error(request, 'يرجى ملء الحقول المطلوبة')
    
    return render(request, 'store/page_form.html', {'action': 'create'})

@manager_required
def page_edit(request: HttpRequest, slug: str) -> HttpResponse:
    """Edit an existing page"""
    page = get_object_or_404(Page, slug=slug)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        excerpt = request.POST.get('excerpt', '').strip()
        status = request.POST.get('status', 'draft')
        seo_title = request.POST.get('seo_title', '').strip()
        seo_description = request.POST.get('seo_description', '').strip()
        seo_keywords = request.POST.get('seo_keywords', '').strip()
        
        if title and content:
            page.title = title
            page.content = content
            page.excerpt = excerpt
            page.status = status
            page.seo_title = seo_title
            page.seo_description = seo_description
            page.seo_keywords = seo_keywords
            
            if status == 'published' and not page.published_at:
                page.published_at = timezone.now()
            elif status != 'published':
                page.published_at = None
                
            page.save()
            
            messages.success(request, 'تم تحديث الصفحة بنجاح')
            return redirect('page_detail', slug=page.slug)
        else:
            messages.error(request, 'يرجى ملء الحقول المطلوبة')
    
    context = {
        'page': page,
        'action': 'edit',
    }
    return render(request, 'store/page_form.html', context)

@manager_required
def page_delete(request: HttpRequest, slug: str) -> HttpResponse:
    """Delete a page"""
    page = get_object_or_404(Page, slug=slug)
    
    if request.method == 'POST':
        page.delete()
        messages.success(request, 'تم حذف الصفحة بنجاح')
        return redirect('page_list')
    
    context = {
        'page': page,
    }
    return render(request, 'store/page_confirm_delete.html', context)

# Article Views
def article_list(request: HttpRequest) -> HttpResponse:
    """List published articles"""
    articles = Article.objects.filter(status='published').order_by('-published_at')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )
    
    # Filter by type
    type_filter = request.GET.get('type')
    if type_filter:
        articles = articles.filter(article_type=type_filter)
    
    # Filter by author
    author_filter = request.GET.get('author')
    if author_filter:
        articles = articles.filter(author__username__icontains=author_filter)
    
    paginator = Paginator(articles, 6)  # Show 6 articles per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get popular articles (by views)
    popular_articles = Article.objects.filter(status='published').order_by('-views')[:5]
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'type_filter': type_filter,
        'author_filter': author_filter,
        'popular_articles': popular_articles,
    }
    return render(request, 'store/article_list.html', context)

def article_detail(request: HttpRequest, slug: str) -> HttpResponse:
    """Display an article"""
    article = get_object_or_404(Article, slug=slug, status='published')
    
    # Increment view count
    article.views += 1
    article.save(update_fields=['views'])
    
    # Get approved comments for this article
    comments = Comment.objects.filter(article=article, status='approved').order_by('-created_at')
    
    # Get related articles (same type)
    related_articles = Article.objects.filter(
        article_type=article.article_type, 
        status='published'
    ).exclude(id=article.id).order_by('-published_at')[:3]
    
    # Handle comment submission
    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content', '').strip()
        if content:
            Comment.objects.create(
                content=content,
                author=request.user,
                article=article,
                status='pending'
            )
            messages.success(request, 'تم إرسال تعليقك بنجاح وسينشر بعد المراجعة')
        else:
            messages.error(request, 'يرجى كتابة تعليق')
    
    context = {
        'article': article,
        'comments': comments,
        'related_articles': related_articles,
    }
    return render(request, 'store/article_detail.html', context)

@manager_required
def article_list_manager(request: HttpRequest) -> HttpResponse:
    """List all articles for managers"""
    articles = Article.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        articles = articles.filter(status=status_filter)
    
    # Filter by type
    type_filter = request.GET.get('type')
    if type_filter:
        articles = articles.filter(article_type=type_filter)
    
    paginator = Paginator(articles, 10)  # Show 10 articles per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'type_filter': type_filter,
    }
    return render(request, 'store/article_list_manager.html', context)

@manager_required
def article_create(request: HttpRequest) -> HttpResponse:
    """Create a new article"""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        excerpt = request.POST.get('excerpt', '').strip()
        article_type = request.POST.get('article_type', 'blog')
        status = request.POST.get('status', 'draft')
        seo_title = request.POST.get('seo_title', '').strip()
        seo_description = request.POST.get('seo_description', '').strip()
        seo_keywords = request.POST.get('seo_keywords', '').strip()
        
        if title and content:
            # Generate slug from title
            slug = slugify(title)
            # Ensure slug is unique
            original_slug = slug
            counter = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            article = Article.objects.create(
                title=title,
                slug=slug,
                content=content,
                excerpt=excerpt,
                author=request.user,
                article_type=article_type,
                status=status,
                seo_title=seo_title,
                seo_description=seo_description,
                seo_keywords=seo_keywords,
            )
            
            if status == 'published':
                article.published_at = timezone.now()
                article.save()
            
            messages.success(request, 'تم إنشاء المقال بنجاح')
            return redirect('article_detail', slug=article.slug)
        else:
            messages.error(request, 'يرجى ملء الحقول المطلوبة')
    
    return render(request, 'store/article_form.html', {'action': 'create'})

@manager_required
def article_edit(request: HttpRequest, slug: str) -> HttpResponse:
    """Edit an existing article"""
    article = get_object_or_404(Article, slug=slug)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        excerpt = request.POST.get('excerpt', '').strip()
        article_type = request.POST.get('article_type', 'blog')
        status = request.POST.get('status', 'draft')
        seo_title = request.POST.get('seo_title', '').strip()
        seo_description = request.POST.get('seo_description', '').strip()
        seo_keywords = request.POST.get('seo_keywords', '').strip()
        
        if title and content:
            article.title = title
            article.content = content
            article.excerpt = excerpt
            article.article_type = article_type
            article.status = status
            article.seo_title = seo_title
            article.seo_description = seo_description
            article.seo_keywords = seo_keywords
            
            if status == 'published' and not article.published_at:
                article.published_at = timezone.now()
            elif status != 'published':
                article.published_at = None
                
            article.save()
            
            messages.success(request, 'تم تحديث المقال بنجاح')
            return redirect('article_detail', slug=article.slug)
        else:
            messages.error(request, 'يرجى ملء الحقول المطلوبة')
    
    context = {
        'article': article,
        'action': 'edit',
    }
    return render(request, 'store/article_form.html', context)

@manager_required
def article_delete(request: HttpRequest, slug: str) -> HttpResponse:
    """Delete an article"""
    article = get_object_or_404(Article, slug=slug)
    
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'تم حذف المقال بنجاح')
        return redirect('article_list_manager')
    
    context = {
        'article': article,
    }
    return render(request, 'store/article_confirm_delete.html', context)

# Landing Page Views
@manager_required
def landing_page_list(request: HttpRequest) -> HttpResponse:
    """List all landing pages"""
    landing_pages = LandingPage.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        landing_pages = landing_pages.filter(
            Q(name__icontains=search_query) | 
            Q(title__icontains=search_query) |
            Q(campaign_name__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        landing_pages = landing_pages.filter(status=status_filter)
    
    paginator = Paginator(landing_pages, 10)  # Show 10 landing pages per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'store/landing_page_list.html', context)

@manager_required
def landing_page_create(request: HttpRequest) -> HttpResponse:
    """Create a new landing page"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        title = request.POST.get('title', '').strip()
        subtitle = request.POST.get('subtitle', '').strip()
        content = request.POST.get('content', '').strip()
        call_to_action = request.POST.get('call_to_action', '').strip()
        call_to_action_url = request.POST.get('call_to_action_url', '').strip()
        status = request.POST.get('status', 'draft')
        campaign_name = request.POST.get('campaign_name', '').strip()
        
        if name and title:
            # Generate slug from name
            slug = slugify(name)
            # Ensure slug is unique
            original_slug = slug
            counter = 1
            while LandingPage.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            landing_page = LandingPage.objects.create(
                name=name,
                slug=slug,
                title=title,
                subtitle=subtitle,
                content=content,
                call_to_action=call_to_action,
                call_to_action_url=call_to_action_url,
                status=status,
                campaign_name=campaign_name,
            )
            
            messages.success(request, 'تم إنشاء صفحة الهبوط بنجاح')
            return redirect('landing_page_detail', slug=landing_page.slug)
        else:
            messages.error(request, 'يرجى ملء الحقول المطلوبة')
    
    return render(request, 'store/landing_page_form.html', {'action': 'create'})

@manager_required
def landing_page_edit(request: HttpRequest, slug: str) -> HttpResponse:
    """Edit an existing landing page"""
    landing_page = get_object_or_404(LandingPage, slug=slug)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        title = request.POST.get('title', '').strip()
        subtitle = request.POST.get('subtitle', '').strip()
        content = request.POST.get('content', '').strip()
        call_to_action = request.POST.get('call_to_action', '').strip()
        call_to_action_url = request.POST.get('call_to_action_url', '').strip()
        status = request.POST.get('status', 'draft')
        campaign_name = request.POST.get('campaign_name', '').strip()
        
        if name and title:
            landing_page.name = name
            landing_page.title = title
            landing_page.subtitle = subtitle
            landing_page.content = content
            landing_page.call_to_action = call_to_action
            landing_page.call_to_action_url = call_to_action_url
            landing_page.status = status
            landing_page.campaign_name = campaign_name
            
            landing_page.save()
            
            messages.success(request, 'تم تحديث صفحة الهبوط بنجاح')
            return redirect('landing_page_detail', slug=landing_page.slug)
        else:
            messages.error(request, 'يرجى ملء الحقول المطلوبة')
    
    context = {
        'landing_page': landing_page,
        'action': 'edit',
    }
    return render(request, 'store/landing_page_form.html', context)

def landing_page_detail(request: HttpRequest, slug: str) -> HttpResponse:
    """Display a landing page"""
    landing_page = get_object_or_404(LandingPage, slug=slug, status='active')
    
    # Check if landing page is active within date range
    now = timezone.now()
    if landing_page.starts_at and landing_page.starts_at > now:
        messages.error(request, 'هذه الصفحة غير متوفرة بعد')
        return redirect('home')
    
    if landing_page.ends_at and landing_page.ends_at < now:
        messages.error(request, 'هذه الصفحة غير متوفرة anymore')
        return redirect('home')
    
    context = {
        'landing_page': landing_page,
    }
    return render(request, 'store/landing_page_detail.html', context)

@manager_required
def landing_page_delete(request: HttpRequest, slug: str) -> HttpResponse:
    """Delete a landing page"""
    landing_page = get_object_or_404(LandingPage, slug=slug)
    
    if request.method == 'POST':
        landing_page.delete()
        messages.success(request, 'تم حذف صفحة الهبوط بنجاح')
        return redirect('landing_page_list')
    
    context = {
        'landing_page': landing_page,
    }
    return render(request, 'store/landing_page_confirm_delete.html', context)

# Comment Views
@manager_required
def comment_list(request: HttpRequest) -> HttpResponse:
    """List all comments for managers"""
    comments = Comment.objects.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        comments = comments.filter(status=status_filter)
    
    # Filter by content type
    content_type_filter = request.GET.get('content_type')
    if content_type_filter:
        if content_type_filter == 'article':
            comments = comments.filter(article__isnull=False)
        elif content_type_filter == 'page':
            comments = comments.filter(page__isnull=False)
    
    paginator = Paginator(comments, 20)  # Show 20 comments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'content_type_filter': content_type_filter,
    }
    return render(request, 'store/comment_list.html', context)

@manager_required
def comment_update_status(request: HttpRequest, comment_id: int) -> HttpResponse:
    """Update comment status"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Comment.COMMENT_STATUS).keys():
            comment.status = status
            comment.save()
            messages.success(request, 'تم تحديث حالة التعليق بنجاح')
        else:
            messages.error(request, 'حالة غير صالحة')
    
    return redirect('comment_list')

@manager_required
def comment_delete(request: HttpRequest, comment_id: int) -> HttpResponse:
    """Delete a comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'تم حذف التعليق بنجاح')
        return redirect('comment_list')
    
    context = {
        'comment': comment,
    }
    return render(request, 'store/comment_confirm_delete.html', context)