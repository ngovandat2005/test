import re
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Product, ProductCategory, News, NewsCategory, Banner, Distributor, DealerRegistration, ContactMessage, Project, ConsultationRequest, Catalogue


def home(request):
    banners = Banner.objects.filter(is_active=True)
    featured_products_qs = list(Product.objects.filter(is_featured=True, is_active=True))
    
    # Sắp xếp tùy chỉnh cho featured products: Ưu tiên M7.5 -> M10 -> Jumbo -> Các sản phẩm khác
    def featured_sort(p):
        if 'M7.5' in p.name: return 1
        if 'M10' in p.name: return 2
        if 'Jumbo' in p.name: return 3
        return 4
    featured_products_qs.sort(key=featured_sort)
    featured_products = featured_products_qs[:6]
    
    featured_projects = Project.objects.filter(is_featured=True, is_active=True).order_by('order', '-created_at')[:3]
    
    # Lấy các bài viết phóng sự thực tế (Ưu tiên theo thứ tự sắp xếp)
    phong_su_cat = NewsCategory.objects.filter(slug__in=['phong-su', 'phong-su-thuc-te']).first()
    if phong_su_cat:
        phong_su_db = list(News.objects.filter(category=phong_su_cat, is_active=True).order_by('order', '-published_at', '-id'))
    else:
        phong_su_db = []

    # Danh sách video mặc định phong phú
    default_videos = [
        {
            'title': 'Khảo sát chất lượng vữa khô trộn sẵn tại công trình',
            'channel': 'Keo Vữa Sông Hồng - SHK Mortar',
            'video_id': 'QZ9jP3b47xU',
            'thumb': 'https://images.unsplash.com/photo-1541888946425-d0fbb18086f6?w=600&auto=format&fit=crop&q=80',
            'tag': 'SHK',
            'tag_bg': '#FF7E2E',
        },
        {
            'title': '(Công trình thực tế) Phản hồi thợ xây khi dùng vữa khô SHK',
            'channel': 'Keo Vữa Sông Hồng - SHK Mortar',
            'video_id': 'N-FLw-piwlc',
            'thumb': 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=600&auto=format&fit=crop&q=80',
            'tag': 'SHK',
            'tag_bg': '#FF7E2E',
        },
        {
            'title': 'Công ty TNHH Keo Vữa Sông Hồng - SHK Mortar TVC 2025',
            'channel': 'Keo Vữa Sông Hồng - SHK Mortar',
            'video_id': 'N-FLw-piwlc',
            'thumb': 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=600&auto=format&fit=crop&q=80',
            'tag': 'SHK',
            'tag_bg': '#FF7E2E',
        },
        {
            'title': 'Vữa khô SHK, sản phẩm hướng tới tương lai #vuakhotronsan',
            'channel': 'Mortar keovuasonghong',
            'video_id': 'N-FLw-piwlc',
            'thumb': 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=600&auto=format&fit=crop&q=80',
            'tag': 'SHK',
            'tag_bg': '#6F8A3A',
        },
        {
            'title': 'Quy trình kiểm định và thử nghiệm độ bám dính keo dán gạch SHK',
            'channel': 'Keo Vữa Sông Hồng - SHK Mortar',
            'video_id': 'N-FLw-piwlc',
            'thumb': 'https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?w=600&auto=format&fit=crop&q=80',
            'tag': 'SHK',
            'tag_bg': '#FF7E2E',
        },
        {
            'title': 'Giải pháp vữa xây trát chuyên dụng cho tường gạch nhẹ AAC & ALC',
            'channel': 'Keo Vữa Sông Hồng - SHK Mortar',
            'video_id': 'N-FLw-piwlc',
            'thumb': 'https://images.unsplash.com/photo-1513694203232-719a280e022f?w=600&auto=format&fit=crop&q=80',
            'tag': 'SHK',
            'tag_bg': '#8C5A2B',
        },
        {
            'title': 'Thử nghiệm độ dẻo và tính công tác của vữa tô tường cao cấp SHK',
            'channel': 'Keo Vữa Sông Hồng - SHK Mortar',
            'video_id': 'N-FLw-piwlc',
            'thumb': 'https://images.unsplash.com/photo-1541888946425-d0fbb18086f6?w=600&auto=format&fit=crop&q=80',
            'tag': 'SHK',
            'tag_bg': '#FF7E2E',
        },
        {
            'title': 'Toàn cảnh dây chuyền sấy và đóng bao cát sạch tự động 100%',
            'channel': 'Keo Vữa Sông Hồng - SHK Mortar',
            'video_id': 'N-FLw-piwlc',
            'thumb': 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=600&auto=format&fit=crop&q=80',
            'tag': 'SHK',
            'tag_bg': '#8C5A2B',
        },
        {
            'title': 'Ứng dụng keo dán gạch khổ lớn C2 tại khu biệt thự cao cấp',
            'channel': 'Keo Vữa Sông Hồng - SHK Mortar',
            'video_id': 'N-FLw-piwlc',
            'thumb': 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=600&auto=format&fit=crop&q=80',
            'tag': 'SHK',
            'tag_bg': '#6F8A3A',
        },
        {
            'title': 'Phỏng vấn kỹ sư công trình về hiệu quả rút ngắn tiến độ với vữa trộn sẵn',
            'channel': 'Keo Vữa Sông Hồng - SHK Mortar',
            'video_id': 'N-FLw-piwlc',
            'thumb': 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=600&auto=format&fit=crop&q=80',
            'tag': 'SHK',
            'tag_bg': '#FF7E2E',
        },
        {
            'title': 'Hướng dẫn kỹ thuật trộn vữa và dán gạch chống trượt cho sàn hồ bơi',
            'channel': 'Keo Vữa Sông Hồng - SHK Mortar',
            'video_id': 'N-FLw-piwlc',
            'thumb': 'https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?w=600&auto=format&fit=crop&q=80',
            'tag': 'SHK',
            'tag_bg': '#6F8A3A',
        },
        {
            'title': 'Lễ ký kết hợp tác cung ứng vật tư xây dựng cho các dự án trọng điểm 2026',
            'channel': 'Keo Vữa Sông Hồng - SHK Mortar',
            'video_id': 'N-FLw-piwlc',
            'thumb': 'https://images.unsplash.com/photo-1513694203232-719a280e022f?w=600&auto=format&fit=crop&q=80',
            'tag': 'SHK',
            'tag_bg': '#8C5A2B',
        },
    ]

    all_video_items = []
    # Các bài viết admin tạo mới LUÔN ĐƯỢC ƯU TIÊN HIỆN ĐẦU TIÊN
    for n in phong_su_db:
        vid_id = n.get_video_id() if hasattr(n, 'get_video_id') else 'N-FLw-piwlc'
        thumb = n.image.url if n.image else (f'https://img.youtube.com/vi/{vid_id}/hqdefault.jpg' if vid_id and vid_id != 'N-FLw-piwlc' else 'https://images.unsplash.com/photo-1541888946425-d0fbb18086f6?w=600&auto=format&fit=crop&q=80')
        all_video_items.append({
            'title': n.title,
            'channel': 'Keo Vữa Sông Hồng - SHK Mortar',
            'video_id': vid_id,
            'thumb': thumb,
            'tag': 'SHK',
            'tag_bg': '#FF7E2E',
            'news_slug': n.slug,
        })
    
    # Bổ sung video để đủ ít nhất 4 trang (mỗi trang 6 video)
    for d in default_videos:
        if len(all_video_items) < 24:
            if not any(item['title'] == d['title'] for item in all_video_items):
                all_video_items.append(d)

    # Chia thành các trang 6 video
    phong_su_pages = [all_video_items[i:i + 6] for i in range(0, len(all_video_items), 6)]
    if not phong_su_pages:
        phong_su_pages = [default_videos[:6]]

    context = {
        'banners': banners,
        'featured_products': featured_products,
        'featured_projects': featured_projects,
        'phong_su_pages': phong_su_pages,
    }
    return render(request, 'main/home.html', context)


def about(request):
    return render(request, 'main/about.html')


def product_list(request):
    preferred_order = ['vua-kho-tron-san', 'vua-xay-trat-aac', 'keo-dan-gach-da', 'cat-sach-say-kho']
    all_cats = list(ProductCategory.objects.all())
    categories = sorted(all_cats, key=lambda c: preferred_order.index(c.slug) if c.slug in preferred_order else 99)
    
    cat_meta = {
        'vua-kho-tron-san': {'img': 'img/Vua_kho_chon_san.png', 'name': 'Vữa khô trộn sẵn'},
        'vua-xay-trat-aac': {'img': 'img/Vua_kho.png', 'name': 'Vữa xây AAC'},
        'keo-dan-gach-da': {'img': 'img/keo_dan_gach_c1.png', 'name': 'Keo dán gạch'},
        'cat-sach-say-kho': {'img': 'img/Cat_say.png', 'name': 'Cát sấy khô'},
    }
    
    category_list = []
    for cat in categories:
        meta = cat_meta.get(cat.slug, {'img': 'img/Vua_kho_chon_san.png', 'name': cat.name})
        prods = list(Product.objects.filter(category=cat, is_active=True))
        
        # Sắp xếp tùy chỉnh cho Vữa khô trộn sẵn: M7.5 -> M10 -> Jumbo
        if cat.slug == 'vua-kho-tron-san':
            def custom_sort(p):
                if 'M7.5' in p.name: return 1
                if 'M10' in p.name: return 2
                if 'Jumbo' in p.name: return 3
                return 4
            prods.sort(key=custom_sort)
            
        category_list.append({
            'slug': cat.slug,
            'name': meta['name'],
            'image': meta['img'],
            'products': prods,
            'count': len(prods),
        })
        
    all_products = list(Product.objects.filter(is_active=True))
    cat_slug = request.GET.get('category', '')
    
    return render(request, 'main/product_list.html', {
        'category_list': category_list,
        'all_products': all_products,
        'selected_cat_slug': cat_slug,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    category_products = Product.objects.filter(category=product.category, is_active=True) if product.category else [product]
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]
    related_projects = product.project_set.filter(is_active=True)[:3]
    related_catalogues = product.related_catalogues.filter(is_active=True)[:3]
    return render(request, 'main/product_detail.html', {
        'product': product,
        'category_products': category_products,
        'related': related,
        'related_projects': related_projects,
        'related_catalogues': related_catalogues,
    })


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def news_list(request):
    preferred_order = ['phong-su-thuc-te', 'kien-thuc-chuyen-mon', 'van-hoa-doanh-nghiep']
    categories = list(NewsCategory.objects.all())
    categories.sort(key=lambda c: preferred_order.index(c.slug) if c.slug in preferred_order else 99)
    
    cat_slug = request.GET.get('category', '')
    if cat_slug:
        category = get_object_or_404(NewsCategory, slug=cat_slug)
        news_qs = News.objects.filter(category=category, is_active=True).order_by('order', '-published_at', '-id')
    else:
        category = None
        news_qs = News.objects.filter(is_active=True).order_by('order', '-published_at', '-id')
        
    paginator = Paginator(news_qs, 9)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.get_page(page_number)
    except (EmptyPage, PageNotAnInteger):
        page_obj = paginator.get_page(1)
        
    news_items = page_obj

    return render(request, 'main/news_list.html', {
        'news_items': news_items,
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category,
        'selected_cat_slug': cat_slug,
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


VIETNAM_PROVINCES = [
    'Hà Nội', 'Vĩnh Phúc', 'Bắc Ninh', 'Hưng Yên', 'Hà Nam', 
    'Hải Dương', 'Hải Phòng', 'Thái Bình', 'Nam Định', 'Ninh Bình', 
    'Phú Thọ', 'Lào Cai', 'Yên Bái',
    'An Giang', 'Bà Rịa - Vũng Tàu', 'Bắc Giang', 'Bắc Kạn', 'Bạc Liêu', 
    'Bến Tre', 'Bình Định', 'Bình Dương', 'Bình Phước', 'Bình Thuận', 
    'Cà Mau', 'Cần Thơ', 'Cao Bằng', 'Đà Nẵng', 'Đắk Lắk', 'Đắk Nông', 
    'Điện Biên', 'Đồng Nai', 'Đồng Tháp', 'Gia Lai', 'Hà Giang', 'Hà Tĩnh', 
    'Hậu Giang', 'Hòa Bình', 'Khánh Hòa', 'Kiên Giang', 'Kon Tum', 
    'Lai Châu', 'Lâm Đồng', 'Lạng Sơn', 'Long An', 'Nghệ An', 'Ninh Thuận', 
    'Phú Yên', 'Quảng Bình', 'Quảng Nam', 'Quảng Ngãi', 'Quảng Ninh', 
    'Quảng Trị', 'Sóc Trăng', 'Sơn La', 'Tây Ninh', 'Thái Nguyên', 
    'Thanh Hóa', 'Thừa Thiên Huế', 'Tiền Giang', 'TP Hồ Chí Minh', 
    'Trà Vinh', 'Tuyên Quang', 'Vĩnh Long'
]


def distributors(request):
    province = request.GET.get('province', '')
    all_distributors = list(Distributor.objects.filter(is_active=True).order_by('province', 'name'))
    return render(request, 'main/distributors.html', {
        'distributors': all_distributors,
        'provinces': VIETNAM_PROVINCES,
        'selected_province': province,
    })


def dealer_register(request):
    if request.method == 'POST':
        company = request.POST.get('company', '').strip()
        tax_id = request.POST.get('tax_id', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        province = request.POST.get('province_name', '').strip() or request.POST.get('province', '').strip()
        district = request.POST.get('district_name', '').strip() or request.POST.get('district', '').strip()
        ward = request.POST.get('ward_name', '').strip() or request.POST.get('ward', '').strip()
        note = request.POST.get('note', '').strip()

        address_parts = [p for p in [ward, district, province] if p]
        address = ", ".join(address_parts) if address_parts else province
        products = request.POST.getlist('products_distributed')
        products_distributed = ", ".join(products)

        if company and phone and province:
            DealerRegistration.objects.create(
                company=company, tax_id=tax_id, full_name=full_name,
                phone=phone, email=email if email else None,
                address=address, province=province,
                products_distributed=products_distributed,
                note=note if note else None
            )
            # Gửi email thông báo về admin
            try:
                admin_link = 'http://192.168.1.103:8000/admin/main/dealerregistration/'
                subject = f'[SHK] Đăng ký đại lý – {company}'
                rows = [
                    ('Doanh nghiệp', company),
                    ('Người đại diện', full_name or '(chưa điền)'),
                    ('Mã số thuế', tax_id or '(chưa điền)'),
                    ('Điện thoại', phone),
                    ('Email', email or '(chưa điền)'),
                    ('Khu vực', address or province),
                    ('Sản phẩm', products_distributed or '(chưa chọn)'),
                    ('Ghi chú', note or '(không có)'),
                ]
                body = (
                    'Có đăng ký đại lý mới từ website SHK Mortar:\n\n'
                    + '\n'.join(f'{label}: {value}' for label, value in rows)
                    + f'\n\nVào admin để xem chi tiết: {admin_link}'
                )
                rows_html = ''.join(
                    f'<tr><td style="padding:6px 16px 6px 0;color:#666;white-space:nowrap;vertical-align:top;">{label}</td>'
                    f'<td style="padding:6px 0;color:#111;font-weight:600;">{value}</td></tr>'
                    for label, value in rows
                )
                html_body = f'''
                <div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;">
                    <h2 style="color:#1a2a5e;border-bottom:2px solid #f26522;padding-bottom:10px;">Đăng ký đại lý</h2>
                    <table style="width:100%;border-collapse:collapse;font-size:14px;margin-top:10px;">
                        {rows_html}
                    </table>
                    <p style="margin-top:20px;">
                        <a href="{admin_link}" style="color:#f26522;">Vào admin để xem chi tiết</a>
                    </p>
                    <p style="color:#999;font-size:12px;margin-top:10px;border-top:1px solid #eee;padding-top:10px;">
                        Thời gian đăng ký: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}
                    </p>
                </div>
                '''
                send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.NOTIFY_EMAIL],
                          fail_silently=True, html_message=html_body)
            except Exception:
                pass
            messages.success(request, 'Đăng ký đại lý thành công! Chúng tôi sẽ liên hệ với bạn sớm nhất.')
            return redirect('dealer_register')
        else:
            messages.error(request, 'Vui lòng điền đầy đủ thông tin bắt buộc.')
    all_products = Product.objects.filter(is_active=True).order_by('name')
    return render(request, 'main/dealer_register.html', {'all_products': all_products})


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


from django.core.paginator import Paginator

def project_list(request):
    cat = request.GET.get('category', '')
    projects = Project.objects.filter(is_active=True).order_by('order', '-is_featured', '-created_at')
    
    if cat:
        projects = projects.filter(category=cat)
        
    paginator = Paginator(projects, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'main/project_list.html', {
        'projects': page_obj.object_list,
        'page_obj': page_obj,
        'current_category': cat,
    })


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug, is_active=True)
    related_catalogues = project.related_catalogues.filter(is_active=True)[:3]
    return render(request, 'main/project_detail.html', {
        'project': project,
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

        # Gửi email thông báo về admin
        try:
            subject = f'[SHK] Đăng ký tư vấn mới – {full_name} ({phone_cleaned})'
            body = (
                f'Có đăng ký tư vấn mới từ website SHK Mortar:\n\n'
                f'Họ tên      : {full_name}\n'
                f'Điện thoại  : {phone_cleaned}\n'
                f'Email       : {email or "(chưa điền)"}\n'
                f'Công ty     : {company or "(chưa điền)"}\n'
                f'Khu vực     : {area_full or "(chưa điền)"}\n'
                f'Quan tâm    : {interest or "(chưa điền)"}\n'
                f'Nội dung    : {message_text or "(không có)"}\n\n'
                f'Vào admin để xem chi tiết: http://192.168.1.103:8000/admin/main/consultationrequest/'
            )
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.NOTIFY_EMAIL], fail_silently=True)
        except Exception:
            pass

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
