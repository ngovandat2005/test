from django.contrib import admin
from .models import (ProductCategory, Product, NewsCategory, News,
                     Banner, Distributor, DealerRegistration, ContactMessage,
                     Project, ConsultationRequest, Catalogue)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_featured', 'is_active', 'created_at']
    list_filter = ['category', 'is_featured', 'is_active']
    list_editable = ['is_featured', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active']
    list_editable = ['order', 'is_active']


@admin.register(Distributor)
class DistributorAdmin(admin.ModelAdmin):
    list_display = ['name', 'province', 'phone', 'is_active']
    list_filter = ['province', 'is_active']
    list_editable = ['is_active']
    search_fields = ['name', 'province', 'phone']


@admin.register(DealerRegistration)
class DealerRegistrationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'company', 'phone', 'province', 'created_at', 'is_processed']
    list_filter = ['province', 'is_processed']
    list_editable = ['is_processed']
    search_fields = ['full_name', 'phone', 'company']
    readonly_fields = ['created_at']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'email', 'created_at', 'is_read']
    list_editable = ['is_read']
    readonly_fields = ['created_at']
    search_fields = ['full_name', 'phone']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'client', 'location', 'is_featured', 'is_active', 'created_at']
    list_filter = ['category', 'is_featured', 'is_active']
    list_editable = ['is_featured', 'is_active']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'client', 'location']
    filter_horizontal = ['products_used']


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'company', 'interest', 'created_at', 'is_processed']
    list_filter = ['is_processed']
    list_editable = ['is_processed']
    readonly_fields = ['created_at']
    search_fields = ['full_name', 'phone', 'company']
    actions = ['export_to_excel_action', 'export_to_word_action']

    @admin.action(description="📥 Xuất danh sách đã chọn ra file Excel (.xlsx)")
    def export_to_excel_action(self, request, queryset):
        from django.http import HttpResponse
        from django.utils import timezone
        from .export_utils import export_consultations_to_excel

        wb = export_consultations_to_excel(queryset)
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="Danh_Sach_Tu_Van_{timezone.now().strftime("%Y%m%d_%H%M")}.xlsx"'
        wb.save(response)
        return response

    @admin.action(description="📄 Xuất phiếu tư vấn đã chọn ra file Word (.docx)")
    def export_to_word_action(self, request, queryset):
        from io import BytesIO
        from django.http import HttpResponse
        from django.utils import timezone
        from .export_utils import export_consultation_to_docx
        from docx import Document

        # Tạo file word gộp tất cả phiếu được chọn
        combined_doc = Document()
        first = True
        for obj in queryset:
            if not first:
                combined_doc.add_page_break()
            export_consultation_to_docx(obj, doc=combined_doc)
            first = False

        doc_io = BytesIO()
        combined_doc.save(doc_io)
        doc_io.seek(0)

        response = HttpResponse(
            doc_io.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="Phieu_Dang_Ky_Tu_Van_{timezone.now().strftime("%Y%m%d_%H%M")}.docx"'
        return response



@admin.register(Catalogue)
class CatalogueAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    list_editable = ['is_active']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title']
    filter_horizontal = ['related_products', 'related_projects']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'published_at', 'is_active']
    list_filter = ['category', 'is_active']
    list_editable = ['is_active']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title']
    date_hierarchy = 'published_at'
    filter_horizontal = ['related_products', 'related_projects', 'related_articles']
    fieldsets = [
        (None, {'fields': ['title', 'slug', 'category', 'image', 'video_url', 'summary', 'content', 'published_at', 'is_active']}),
        ('Liên quan', {'fields': ['related_products', 'related_projects', 'related_articles'], 'classes': ['collapse']}),
    ]
