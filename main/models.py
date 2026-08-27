from django.db import models
from django.utils.text import slugify


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
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Danh mục")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Hình ảnh")
    short_description = models.TextField(blank=True, verbose_name="Mô tả ngắn")
    description = models.TextField(blank=True, verbose_name="Mô tả chi tiết")
    specifications = models.TextField(blank=True, verbose_name="Thông số kỹ thuật")
    is_featured = models.BooleanField(default=False, verbose_name="Sản phẩm nổi bật")
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"
        ordering = ['-is_featured', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


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
    published_at = models.DateField(verbose_name="Ngày đăng")
    related_products = models.ManyToManyField('Product', blank=True, verbose_name="Sản phẩm liên quan", related_name='related_news')
    related_projects = models.ManyToManyField('Project', blank=True, verbose_name="Dự án liên quan", related_name='related_news')
    related_articles = models.ManyToManyField('self', blank=True, verbose_name="Bài viết liên quan", symmetrical=False)
    video_url = models.URLField(blank=True, null=True, verbose_name="URL YouTube", help_text="Dán link YouTube video phóng sự")
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị")

    class Meta:
        verbose_name = "Tin tức"
        verbose_name_plural = "Tin tức"
        ordering = ['-published_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def video_embed_url(self):
        if not self.video_url:
            return None
        url = self.video_url.strip()
        if 'youtu.be/' in url:
            vid = url.split('youtu.be/')[-1].split('?')[0].split('&')[0]
        elif 'youtube.com/watch' in url:
            import urllib.parse
            qs = urllib.parse.urlparse(url).query
            vid = urllib.parse.parse_qs(qs).get('v', [None])[0]
        elif 'youtube.com/embed/' in url:
            vid = url.split('youtube.com/embed/')[-1].split('?')[0]
        else:
            return None
        return f'https://www.youtube.com/embed/{vid}' if vid else None

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
    full_name = models.CharField(max_length=200, verbose_name="Họ tên")
    company = models.CharField(max_length=300, blank=True, verbose_name="Tên công ty/cửa hàng")
    phone = models.CharField(max_length=20, verbose_name="Số điện thoại")
    email = models.EmailField(blank=True, verbose_name="Email")
    address = models.TextField(verbose_name="Địa chỉ")
    province = models.CharField(max_length=100, verbose_name="Tỉnh/Thành phố")
    note = models.TextField(blank=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False, verbose_name="Đã xử lý")

    class Meta:
        verbose_name = "Đăng ký đại lý"
        verbose_name_plural = "Đăng ký đại lý"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.phone}"


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
    is_featured = models.BooleanField(default=False, verbose_name="Dự án nổi bật")
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dự án"
        verbose_name_plural = "Dự án"
        ordering = ['-is_featured', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

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
    related_products = models.ManyToManyField('Product', blank=True, verbose_name="Sản phẩm liên quan", related_name='related_catalogues')
    related_projects = models.ManyToManyField('Project', blank=True, verbose_name="Dự án liên quan", related_name='related_catalogues')
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Catalogue"
        verbose_name_plural = "Catalogue"
        ordering = ['category', 'title']

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
