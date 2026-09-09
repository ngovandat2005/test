from django.db import models
from django.utils.text import slugify


def youtube_embed_url(url):
    if not url:
        return None
    url = url.strip()
    if 'youtu.be/' in url:
        vid = url.split('youtu.be/')[-1].split('?')[0].split('&')[0]
    elif 'youtube.com/watch' in url:
        import urllib.parse
        qs = urllib.parse.urlparse(url).query
        vid = urllib.parse.parse_qs(qs).get('v', [None])[0]
    elif 'youtube.com/embed/' in url:
        vid = url.split('youtube.com/embed/')[-1].split('?')[0]
    elif 'youtube-nocookie.com/embed/' in url:
        vid = url.split('youtube-nocookie.com/embed/')[-1].split('?')[0]
    else:
        return None
    return f'https://www.youtube-nocookie.com/embed/{vid}?rel=0&enablejsapi=1' if vid else None



class ProductCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = "Danh mục sản phẩm"
        verbose_name_plural = "Danh mục sản phẩm"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=300, verbose_name="Tên sản phẩm")
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name="Mã SKU")
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Danh mục")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Hình ảnh")
    video_url = models.URLField(blank=True, null=True, verbose_name="Link video YouTube")
    ecatalog_file = models.FileField(upload_to='products/ecatalog/', blank=True, null=True, verbose_name="File E-catalog (PDF)")
    certificate_file = models.FileField(upload_to='products/certificates/', blank=True, null=True, verbose_name="Chứng chỉ chất lượng (PDF)")
    short_description = models.TextField(blank=True, verbose_name="Đoạn giới thiệu tổng quan")
    description = models.TextField(blank=True, verbose_name="Hướng dẫn thi công")
    usage_norms = models.TextField(blank=True, verbose_name="Định mức sử dụng")
    specifications = models.TextField(blank=True, verbose_name="Thông tin sản phẩm")
    order = models.IntegerField(default=0, verbose_name="Thứ tự")
    is_featured = models.BooleanField(default=False, verbose_name="Sản phẩm nổi bật")
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"
        ordering = ['order', '-is_featured', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def video_embed_url(self):
        return youtube_embed_url(self.video_url)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    MEDIA_TYPE_CHOICES = [('image', 'Ảnh'), ('video', 'Video')]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery_images')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image', verbose_name="Loại")
    image = models.ImageField(upload_to='products/gallery/', blank=True, null=True, verbose_name="Ảnh (tải lên)")
    image_url = models.URLField(blank=True, null=True, verbose_name="Ảnh (URL ngoài)")
    video_url = models.URLField(blank=True, null=True, verbose_name="Video (URL YouTube)")
    order = models.PositiveIntegerField(default=0, blank=True, verbose_name="Thứ tự")

    class Meta:
        verbose_name = "Ảnh/Video sản phẩm"
        verbose_name_plural = "Ảnh/Video sản phẩm"
        ordering = ['order']

    def display_url(self):
        if self.media_type == 'video':
            return None
        if self.image:
            return self.image.url
        return self.image_url

    def video_embed_url(self):
        if self.media_type != 'video':
            return None
        return youtube_embed_url(self.video_url)

    def __str__(self):
        return f"Media {self.pk}"


class ProductHighlight(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='highlights')
    text = models.CharField(max_length=300, verbose_name="Ý nổi bật")
    order = models.PositiveIntegerField(default=0, blank=True, verbose_name="Thứ tự")

    class Meta:
        verbose_name = "Ưu điểm vượt trội"
        verbose_name_plural = "Ưu điểm vượt trội"
        ordering = ['order']

    def __str__(self):
        return self.text


class ProductSpec(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specs')
    label = models.CharField(max_length=200, verbose_name="Tên thông số")
    value = models.CharField(max_length=300, verbose_name="Giá trị")
    order = models.PositiveIntegerField(default=0, blank=True, verbose_name="Thứ tự")

    class Meta:
        verbose_name = "Thông số sản phẩm"
        verbose_name_plural = "Thông số sản phẩm"
        ordering = ['order']

    def __str__(self):
        return f"{self.label}: {self.value}"


class NewsCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = "Danh mục tin tức"
        verbose_name_plural = "Danh mục tin tức"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class News(models.Model):
    title = models.CharField(max_length=400, verbose_name="Tiêu đề")
    slug = models.SlugField(unique=True, blank=True, max_length=400)
    category = models.ForeignKey(NewsCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Danh mục")
    image = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name="Hình ảnh")
    summary = models.TextField(blank=True, verbose_name="Tóm tắt")
    content = models.TextField(verbose_name="Nội dung")
    
    related_products = models.ManyToManyField('Product', blank=True, verbose_name="Sản phẩm liên quan", related_name='related_news')
    related_projects = models.ManyToManyField('Project', blank=True, verbose_name="Dự án liên quan", related_name='related_news')
    related_articles = models.ManyToManyField('self', blank=True, verbose_name="Bài viết liên quan", symmetrical=False)
    video_url = models.URLField(blank=True, null=True, verbose_name="URL YouTube", help_text="Dán link YouTube video phóng sự")
    author = models.CharField(max_length=200, default='Công ty TNHH Keo Vữa Sông Hồng', verbose_name="Tác giả")
    order = models.IntegerField(default=0, verbose_name="Thứ tự")
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị")
    published_at = models.DateTimeField(verbose_name="Ngày đăng", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Tin tức"
        verbose_name_plural = "Tin tức"
        ordering = ['order', '-published_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def video_embed_url(self):
        return youtube_embed_url(self.video_url)

    def get_video_id(self):
        if not self.video_url:
            return 'N-FLw-piwlc'
        url = self.video_url.strip()
        if 'youtu.be/' in url:
            return url.split('youtu.be/')[-1].split('?')[0].split('&')[0]
        elif 'youtube.com/watch' in url:
            import urllib.parse
            qs = urllib.parse.urlparse(url).query
            v = urllib.parse.parse_qs(qs).get('v', [None])[0]
            return v or 'N-FLw-piwlc'
        elif 'youtube.com/embed/' in url:
            return url.split('youtube.com/embed/')[-1].split('?')[0]
        elif 'youtube-nocookie.com/embed/' in url:
            return url.split('youtube-nocookie.com/embed/')[-1].split('?')[0]
        return 'N-FLw-piwlc'

    def __str__(self):
        return self.title


class Banner(models.Model):
    title = models.CharField(max_length=300, verbose_name="Tiêu đề")
    subtitle = models.CharField(max_length=400, blank=True, verbose_name="Tiêu đề phụ")
    image = models.ImageField(upload_to='banners/', blank=True, null=True, verbose_name="Hình ảnh")
    link = models.CharField(max_length=300, blank=True, verbose_name="Đường dẫn")
    order = models.IntegerField(default=0, verbose_name="Thứ tự")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Banners"
        ordering = ['order']

    def __str__(self):
        return self.title


class Distributor(models.Model):
    name = models.CharField(max_length=300, verbose_name="Tên đại lý")
    address = models.TextField(verbose_name="Địa chỉ")
    province = models.CharField(max_length=100, verbose_name="Tỉnh/Thành phố")
    phone = models.CharField(max_length=20, verbose_name="Số điện thoại")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Đại lý phân phối"
        verbose_name_plural = "Đại lý phân phối"
        ordering = ['province', 'name']

    def __str__(self):
        return f"{self.name} - {self.province}"


class DealerRegistration(models.Model):
    full_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="Họ tên")
    company = models.CharField(max_length=300, verbose_name="Tên doanh nghiệp/Hộ Kinh Doanh")
    tax_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Mã số thuế")
    phone = models.CharField(max_length=20, verbose_name="Số điện thoại")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    address = models.TextField(verbose_name="Địa chỉ trụ sở")
    province = models.CharField(max_length=100, verbose_name="Khu vực đăng ký đại lý")
    products_distributed = models.TextField(blank=True, null=True, verbose_name="Sản phẩm phân phối")
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False, verbose_name="Đã xử lý")

    class Meta:
        verbose_name = "Đăng ký đại lý"
        verbose_name_plural = "Đăng ký đại lý"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company} - {self.phone}"


class ProjectCategory(models.Model):
    name = models.CharField(max_length=200, verbose_name="Tên danh mục")
    slug = models.SlugField(unique=True, blank=True, verbose_name="Slug")

    class Meta:
        verbose_name = "Danh mục dự án"
        verbose_name_plural = "Danh mục dự án"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


PROJECT_CATEGORY_CHOICES = [
    ('dan-dung', 'Dự án dân dụng'),
    ('cong-nghiep', 'Dự án công nghiệp / thương mại'),
]

class Project(models.Model):
    title = models.CharField(max_length=400, verbose_name="Tên dự án")
    slug = models.SlugField(unique=True, blank=True, max_length=400)
    category = models.CharField(max_length=20, choices=PROJECT_CATEGORY_CHOICES, default='dan-dung', verbose_name="Loại dự án")
    client = models.CharField(max_length=300, blank=True, verbose_name="Chủ đầu tư")
    location = models.CharField(max_length=300, blank=True, verbose_name="Địa điểm")
    image = models.ImageField(upload_to='projects/', blank=True, null=True, verbose_name="Hình ảnh")
    description = models.TextField(blank=True, verbose_name="Mô tả dự án")
    products_used = models.ManyToManyField('Product', blank=True, verbose_name="Sản phẩm sử dụng")
    order = models.IntegerField(default=0, verbose_name="Thứ tự")
    is_featured = models.BooleanField(default=False, verbose_name="Dự án nổi bật")
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị")
    author = models.CharField(max_length=200, default='Công ty TNHH Keo Vữa Sông Hồng', verbose_name="Tác giả")
    published_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đăng", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dự án"
        verbose_name_plural = "Dự án"
        ordering = ['order', '-is_featured', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def title_display(self):
        import re
        if re.search(r'\b(c2)\b', self.title, re.IGNORECASE):
            return re.sub(r'(\b[cC]2\b)\s*', r'\1<br>', self.title, count=1)
        return self.title

    def get_category_display(self):
        try:
            cat = ProjectCategory.objects.filter(slug=self.category).first()
            if cat:
                return cat.name
        except Exception:
            pass
        return dict(PROJECT_CATEGORY_CHOICES).get(self.category, self.category)

    @property
    def category_display(self):
        cat_str = self.get_category_display()
        if 'công nghiệp' in cat_str.lower() and 'thương mại' in cat_str.lower():
            import re
            return re.sub(r'\s*/\s*', '<br>', cat_str)
        return cat_str

    def __str__(self):
        return self.title


class ConsultationRequest(models.Model):
    full_name = models.CharField(max_length=200, verbose_name="Họ tên")
    phone = models.CharField(max_length=20, verbose_name="Số điện thoại")
    email = models.EmailField(blank=True, verbose_name="Email")
    company = models.CharField(max_length=300, blank=True, verbose_name="Công ty / Dự án")
    interest = models.CharField(max_length=200, blank=True, verbose_name="Quan tâm đến")
    message = models.TextField(blank=True, verbose_name="Yêu cầu cụ thể")
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False, verbose_name="Đã xử lý")

    class Meta:
        verbose_name = "Đăng ký tư vấn"
        verbose_name_plural = "Đăng ký tư vấn"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.phone}"


CATALOGUE_CATEGORY_CHOICES = [
    ('san-pham', 'Catalogue sản phẩm'),
    ('giai-phap', 'Catalogue giải pháp'),
    ('du-an', 'Catalogue dự án'),
]

class Catalogue(models.Model):
    title = models.CharField(max_length=400, verbose_name="Tiêu đề catalogue")
    slug = models.SlugField(unique=True, blank=True, max_length=400)
    category = models.CharField(max_length=20, choices=CATALOGUE_CATEGORY_CHOICES, default='san-pham', verbose_name="Loại catalogue")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    thumbnail = models.ImageField(upload_to='catalogues/', blank=True, null=True, verbose_name="Ảnh bìa")
    file = models.FileField(upload_to='catalogues/files/', blank=True, null=True, verbose_name="File PDF")
    group_name = models.CharField(max_length=255, blank=True, verbose_name="Tên nhóm tài liệu (VD: Tài liệu keo dán gạch)")
    order = models.IntegerField(default=0, verbose_name="Số thứ tự sắp xếp")
    related_products = models.ManyToManyField('Product', blank=True, verbose_name="Sản phẩm liên quan", related_name='related_catalogues')
    related_projects = models.ManyToManyField('Project', blank=True, verbose_name="Dự án liên quan", related_name='related_catalogues')
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Catalogue"
        verbose_name_plural = "Catalogue"
        ordering = ['order', 'title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    full_name = models.CharField(max_length=200, verbose_name="Họ tên")
    phone = models.CharField(max_length=20, verbose_name="Số điện thoại")
    email = models.EmailField(blank=True, verbose_name="Email")
    message = models.TextField(verbose_name="Nội dung")
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Liên hệ"
        verbose_name_plural = "Liên hệ"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.phone}"


class ThemeSettings(models.Model):
    # Đầu trang
    header_text = models.CharField(max_length=255, blank=True, null=True, verbose_name="Text đầu trang")
    logo = models.ImageField(upload_to='theme/', blank=True, null=True, verbose_name="Logo công ty")
    show_megamenu = models.BooleanField(default=False, verbose_name="Hiển thị megamenu")
    hotline_1 = models.CharField(max_length=50, blank=True, null=True, verbose_name="Hotline 1")
    hotline_2 = models.CharField(max_length=50, blank=True, null=True, verbose_name="Hotline 2")
    email = models.EmailField(blank=True, null=True, verbose_name="Email liên hệ")
    open_hours = models.CharField(max_length=100, blank=True, null=True, verbose_name="Giờ mở cửa")

    # Trang chủ - Module Giới thiệu
    show_intro = models.BooleanField(default=True, verbose_name="Hiển thị Module Giới thiệu")
    intro_title = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tiêu đề giới thiệu")
    intro_description = models.TextField(blank=True, null=True, verbose_name="Mô tả giới thiệu")
    intro_youtube_url = models.URLField(blank=True, null=True, verbose_name="Link YouTube")

    # Footer
    footer_address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Địa chỉ footer")
    footer_phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="SĐT footer")
    footer_email = models.EmailField(blank=True, null=True, verbose_name="Email footer")
    footer_facebook = models.URLField(blank=True, null=True, verbose_name="Link Facebook")
    footer_zalo = models.URLField(blank=True, null=True, verbose_name="Link Zalo")
    footer_youtube = models.URLField(blank=True, null=True, verbose_name="Link YouTube (Footer)")

    class Meta:
        verbose_name = "Cài đặt Giao diện"
        verbose_name_plural = "Cài đặt Giao diện"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Tùy chỉnh giao diện website"


class HomeBanner(models.Model):
    theme = models.ForeignKey(ThemeSettings, on_delete=models.CASCADE, related_name='banners')
    image = models.ImageField(upload_to='banners/', verbose_name="Hình ảnh banner")
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tiêu đề")
    link = models.URLField(blank=True, null=True, verbose_name="Link liên kết")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự")

    class Meta:
        verbose_name = "Banner Trang chủ"
        verbose_name_plural = "Banners Trang chủ"
        ordering = ['order']

    def __str__(self):
        return self.title or f"Banner {self.pk}"


class Partner(models.Model):
    theme = models.ForeignKey(ThemeSettings, on_delete=models.CASCADE, related_name='partners')
    image = models.ImageField(upload_to='partners/', verbose_name="Logo đối tác")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tên đối tác")
    link = models.URLField(blank=True, null=True, verbose_name="Link liên kết")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự")

    class Meta:
        verbose_name = "Đối tác"
        verbose_name_plural = "Đối tác"
        ordering = ['order']

    def __str__(self):
        return self.name or f"Đối tác {self.pk}"
