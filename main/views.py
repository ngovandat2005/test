import re
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, ProductCategory, News, NewsCategory, Banner, Distributor, DealerRegistration, ContactMessage, Project, ConsultationRequest, Catalogue


def home(request):
    banners = Banner.objects.filter(is_active=True)
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:6]
    featured_projects = Project.objects.filter(is_featured=True, is_active=True)[:3]
    try:
        phong_su_cat = NewsCategory.objects.get(slug='phong-su')
        phong_su_news = News.objects.filter(category=phong_su_cat, is_active=True)[:6]
    except NewsCategory.DoesNotExist:
        phong_su_news = News.objects.none()
    context = {
        'banners': banners,
        'featured_products': featured_products,
        'featured_projects': featured_projects,
        'phong_su_news': phong_su_news,
    }
    return render(request, 'main/home.html', context)


def about(request):
    return render(request, 'main/about.html')


def product_list(request):
    categories = ProductCategory.objects.all()
    cat_slug = request.GET.get('category')
    if cat_slug:
        category = get_object_or_404(ProductCategory, slug=cat_slug)
        products = Product.objects.filter(category=category, is_active=True)
    else:
        category = None
        products = Product.objects.filter(is_active=True)
    return render(request, 'main/product_list.html', {
        'products': products, 'categories': categories, 'current_category': category,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]
    related_projects = product.project_set.filter(is_active=True)[:3]
    related_catalogues = product.related_catalogues.filter(is_active=True)[:3]
    return render(request, 'main/product_detail.html', {
        'product': product,
        'related': related,
        'related_projects': related_projects,
        'related_catalogues': related_catalogues,
    })


def news_list(request):
    categories = NewsCategory.objects.all()
    cat_slug = request.GET.get('category')
    if cat_slug:
        category = get_object_or_404(NewsCategory, slug=cat_slug)
        news_items = News.objects.filter(category=category, is_active=True)
    else:
        category = None
        news_items = News.objects.filter(is_active=True)
    return render(request, 'main/news_list.html', {
        'news_items': news_items, 'categories': categories, 'current_category': category,
    })


def news_detail(request, slug):
    news = get_object_or_404(News, slug=slug, is_active=True)
    related = news.related_articles.filter(is_active=True)[:3]
    if not related:
        related = News.objects.filter(category=news.category, is_active=True).exclude(pk=news.pk)[:3]
    return render(request, 'main/news_detail.html', {
        'news': news,
        'related': related,
        'related_products': news.related_products.filter(is_active=True)[:4],
        'related_projects': news.related_projects.filter(is_active=True)[:3],
    })


def distributors(request):
    province = request.GET.get('province', '')
    all_distributors = Distributor.objects.filter(is_active=True)
    if province:
        all_distributors = all_distributors.filter(province__icontains=province)
    provinces = Distributor.objects.filter(is_active=True).values_list('province', flat=True).distinct().order_by('province')
    return render(request, 'main/distributors.html', {
        'distributors': all_distributors, 'provinces': provinces, 'selected_province': province,
    })


def dealer_register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        company = request.POST.get('company', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()
        province = request.POST.get('province', '').strip()
        note = request.POST.get('note', '').strip()
        if full_name and phone and address and province:
            DealerRegistration.objects.create(
                full_name=full_name, company=company, phone=phone,
                email=email, address=address, province=province, note=note
            )
            messages.success(request, 'Đăng ký đại lý thành công! Chúng tôi sẽ liên hệ với bạn sớm nhất.')
            return redirect('dealer_register')
        else:
            messages.error(request, 'Vui lòng điền đầy đủ thông tin bắt buộc.')
    return render(request, 'main/dealer_register.html')


def contact(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        message_text = request.POST.get('message', '').strip()
        if full_name and phone and message_text:
            ContactMessage.objects.create(full_name=full_name, phone=phone, email=email, message=message_text)
            messages.success(request, 'Cảm ơn bạn đã liên hệ! Chúng tôi sẽ phản hồi sớm nhất.')
            return redirect('contact')
        else:
            messages.error(request, 'Vui lòng điền đầy đủ thông tin.')
    return render(request, 'main/contact.html')


def catalogue(request):
    cat = request.GET.get('category', '')
    catalogues = Catalogue.objects.filter(is_active=True)
    if cat:
        catalogues = catalogues.filter(category=cat)
    return render(request, 'main/catalogue.html', {
        'catalogues': catalogues,
        'current_category': cat,
    })


def project_list(request):
    cat = request.GET.get('category', '')
    projects = Project.objects.filter(is_active=True)
    if cat:
        projects = projects.filter(category=cat)
    return render(request, 'main/project_list.html', {
        'projects': projects,
        'current_category': cat,
    })


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug, is_active=True)
    related = Project.objects.filter(category=project.category, is_active=True).exclude(pk=project.pk)[:3]
    related_catalogues = project.related_catalogues.filter(is_active=True)[:3]
    return render(request, 'main/project_detail.html', {
        'project': project,
        'related': related,
        'related_catalogues': related_catalogues,
    })


def consultation(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        province = request.POST.get('province', '').strip() or request.POST.get('area', '').strip()
        district = request.POST.get('district', '').strip()
        address_detail = request.POST.get('address_detail', '').strip()
        company = request.POST.get('company', '').strip()
        interest = request.POST.get('interest', '').strip()
        message_text = request.POST.get('message', '').strip()

        referer = request.META.get('HTTP_REFERER') or 'home'

        # Check required fields
        if not full_name or not phone or not province or not (interest or message_text):
            messages.error(request, 'Vui lòng điền đầy đủ các thông tin bắt buộc (*).')
            return redirect(referer)

        # Validate phone format (10 digits Vietnam phone number)
        phone_cleaned = re.sub(r'[\s.-]', '', phone)
        if not re.match(r'^(0[235789])[0-9]{8}$', phone_cleaned):
            messages.error(request, 'Số điện thoại không hợp lệ. Vui lòng nhập số điện thoại gồm 10 chữ số (VD: 0912345678).')
            return redirect(referer)

        # Validate email strictly if provided
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9]+([.-][a-zA-Z0-9]+)*\.[a-zA-Z]{2,}$', email):
            messages.error(request, 'Địa chỉ email không đúng định dạng. Vui lòng kiểm tra lại tên miền (VD: example@gmail.com).')
            return redirect(referer)

        # Check duplicate submission within 1 hour
        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_duplicate = ConsultationRequest.objects.filter(
            phone=phone_cleaned,
            created_at__gte=one_hour_ago
        ).exists()

        if recent_duplicate:
            messages.warning(request, 'Thông tin đăng ký của số điện thoại này đã được tiếp nhận gần đây. Đội ngũ chuyên viên của SHK Mortar sẽ liên hệ sớm nhất!')
            return redirect(referer)

        # Build full address string
        area_parts = [p for p in [province, district, address_detail] if p]
        area_full = ", ".join(area_parts)

        full_message_parts = []
        if area_full:
            full_message_parts.append(f"Khu vực: {area_full}")
        if interest or message_text:
            full_message_parts.append(f"Nhu cầu: {interest or message_text}")
        full_message = "\n".join(full_message_parts)

        consultation_obj = ConsultationRequest.objects.create(
            full_name=full_name, phone=phone_cleaned, email=email,
            company=company, interest=interest or province or "Tư vấn sản phẩm", message=full_message
        )
        
        # Tự động xuất và cập nhật ra file Excel và Word
        try:
            from .export_utils import auto_save_consultation_to_files
            auto_save_consultation_to_files(consultation_obj)
        except Exception:
            pass

        messages.success(request, 'Đăng ký tư vấn thành công! Chuyên viên của SHK Mortar sẽ liên hệ với bạn trong thời gian sớm nhất.')
        return redirect(referer)

    products = Product.objects.filter(is_active=True).values('name')
    return render(request, 'main/consultation.html', {'products': products})


def download_consultations_excel(request):
    """Tải file Excel danh sách khách hàng đăng ký tư vấn"""
    from .export_utils import export_consultations_to_excel
    queryset = ConsultationRequest.objects.all().order_by('-created_at')
    wb = export_consultations_to_excel(queryset)
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="Danh_Sach_Dang_Ky_Tu_Van_{timezone.now().strftime("%Y%m%d_%H%M")}.xlsx"'
    wb.save(response)
    return response


def download_consultation_word(request, pk):
    """Tải file Word phiếu yêu cầu tư vấn cho 1 khách hàng cụ thể"""
    from io import BytesIO
    from .export_utils import export_consultation_to_docx
    consultation_obj = get_object_or_404(ConsultationRequest, pk=pk)
    doc = export_consultation_to_docx(consultation_obj)
    
    doc_io = BytesIO()
    doc.save(doc_io)
    doc_io.seek(0)
    
    response = HttpResponse(
        doc_io.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    safe_phone = str(consultation_obj.phone).replace(' ', '')
    response['Content-Disposition'] = f'attachment; filename="Phieu_Tu_Van_SHK_{consultation_obj.pk}_{safe_phone}.docx"'
    return response



CALCULATOR_PRODUCT_MAP = {
    'mortar': ['vua-kho-tron-san', 'vua-tieu-chuan', 'vua-cao-cap'],
    'tile_adhesive': ['keo-dan-gach', 'keo-noi-that', 'keo-ngoai-troi'],
    'sand': ['cat-say', 'cat-0-06mm', 'cat-0-2mm'],
}

def calculator(request):
    result = None
    recommended_products = []
    if request.method == 'POST':
        tool = request.POST.get('tool')
        try:
            if tool == 'mortar':
                area = float(request.POST.get('area', 0))
                thickness = float(request.POST.get('thickness', 10))
                result = {'label': 'Lượng vữa cần dùng', 'value': f'{area * thickness * 1.85:.1f} kg', 'tool': tool, 'tool_name': 'Vữa khô trộn sẵn'}
            elif tool == 'tile_adhesive':
                area = float(request.POST.get('area', 0))
                tile_size = request.POST.get('tile_size', 'small')
                rate = {'small': 4.5, 'medium': 5.5, 'large': 7.0}.get(tile_size, 5.0)
                result = {'label': 'Lượng keo dán gạch cần dùng', 'value': f'{area * rate:.1f} kg', 'tool': tool, 'tool_name': 'Keo dán gạch'}
            elif tool == 'sand':
                area = float(request.POST.get('area', 0))
                thickness = float(request.POST.get('thickness', 10))
                result = {'label': 'Lượng cát cần dùng', 'value': f'{area * (thickness / 1000) * 1600:.1f} kg', 'tool': tool, 'tool_name': 'Cát sấy khô'}
            if result and tool:
                category_slugs = CALCULATOR_PRODUCT_MAP.get(tool, [])
                recommended_products = Product.objects.filter(
                    is_active=True, category__slug__in=category_slugs
                )[:3]
                if not recommended_products:
                    cat_map = {'mortar': 'vua-kho-tron-san', 'tile_adhesive': 'keo-dan-gach', 'sand': 'cat-say'}
                    recommended_products = Product.objects.filter(
                        is_active=True, category__slug=cat_map.get(tool, '')
                    )[:3]
                    if not recommended_products:
                        recommended_products = Product.objects.filter(is_active=True)[:3]
        except (ValueError, ZeroDivisionError):
            messages.error(request, 'Vui lòng nhập số liệu hợp lệ.')
    return render(request, 'main/calculator.html', {'result': result, 'recommended_products': recommended_products})
