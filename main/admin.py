from django import forms
from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import (ProductCategory, Product, ProductImage,
                     NewsCategory, News,
                     Banner, Distributor, DealerRegistration, ContactMessage,
                     Project, ProjectCategory, ConsultationRequest, Catalogue, ThemeSettings,
                     HomeBanner, Partner)


class ThumbnailClearableFileInput(forms.ClearableFileInput):
    template_name = 'admin/main/product/widgets/thumbnail_file_input.html'


@admin.register(ProductCategory)
class ProductCategoryAdmin(ModelAdmin):
    change_list_template = 'admin/main/productcategory/change_list.html'
    change_form_template = 'admin/main/productcategory/change_form.html'
    list_fullwidth = True
    list_display = ['name', 'slug', 'products_count']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

    def products_count(self, obj):
        return obj.product_set.count()
    products_count.short_description = "Số lượng sản phẩm"

    def changelist_view(self, request, extra_context=None):
        if 'list_per_page' in request.GET:
            try:
                per_page = int(request.GET['list_per_page'])
                if per_page in (10, 20, 50, 100):
                    self.list_per_page = per_page
            except (TypeError, ValueError):
                pass
            request.GET = request.GET.copy()
            del request.GET['list_per_page']
        extra_context = extra_context or {}
        extra_context['total_count'] = ProductCategory.objects.count()
        response = super().changelist_view(request, extra_context)
        cl = getattr(response, 'context_data', {}).get('cl')
        if cl is not None:
            page = cl.paginator.page(cl.page_num)
            response.context_data['range_start'] = page.start_index()
            response.context_data['range_end'] = page.end_index()
        return response


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 0
    fields = ['media_type', 'image', 'image_url', 'video_url', 'order']

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'image':
            formfield.widget = forms.FileInput()
        elif db_field.name == 'media_type':
            formfield.widget.attrs['class'] = 'pd-media-type-select'
        return formfield


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    change_list_template = 'admin/main/product/change_list.html'
    change_form_template = 'admin/main/product/change_form.html'
    list_fullwidth = True
    list_display = ['name', 'sku', 'category', 'is_featured', 'is_active', 'created_at']
    list_filter = ['category', 'is_featured', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'sku', 'category__name', 'short_description', 'specifications']
    inlines = [ProductImageInline]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'image':
            formfield.widget = ThumbnailClearableFileInput()
        return formfield

    fieldsets = (
        (None, {'fields': ('name', 'sku', 'slug', 'category', 'order')}),
        ('Media', {'fields': ('image',), 'classes': ('tab-media',)}),
        ('Tài liệu', {'fields': ('ecatalog_file', 'certificate_file'), 'classes': ('tab-media',)}),
        ('Thông tin chung', {'fields': ('short_description',), 'classes': ('tab-general',)}),
        ('Hướng dẫn thi công', {'fields': ('description',), 'classes': ('tab-guide',)}),
        ('Định mức sử dụng', {'fields': ('usage_norms',), 'classes': ('tab-norms',)}),
        ('Thông tin sản phẩm', {'fields': ('specifications',)}),
    )

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('toggle-active/<int:pk>/', self.admin_site.admin_view(self.toggle_active), name='main_product_toggle_active'),
            path('update-order/<int:pk>/', self.admin_site.admin_view(self.update_order), name='main_product_update_order'),
            path('reorder-products/', self.admin_site.admin_view(self.reorder_products), name='main_product_reorder_products'),
            path('reorder-gallery/<int:pk>/', self.admin_site.admin_view(self.reorder_gallery), name='main_product_reorder_gallery'),
        ]
        return custom_urls + urls

    def reorder_products(self, request):
        import json
        from django.http import JsonResponse
        if request.method != 'POST' or not request.user.has_perm('main.change_product'):
            return JsonResponse({'ok': False}, status=403)
        try:
            data = json.loads(request.body)
            pks = data.get('pks', [])
            start_order = int(data.get('start_order', 0))
            for i, pk in enumerate(pks):
                Product.objects.filter(pk=pk).update(order=start_order + i)
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)

    def reorder_gallery(self, request, pk):
        import json
        from django.http import JsonResponse
        if request.method != 'POST' or not request.user.has_perm('main.change_product'):
            return JsonResponse({'ok': False}, status=403)
        try:
            data = json.loads(request.body)
            product = Product.objects.get(pk=pk)
            avatar_id = data.get('avatar_id')
            gallery_order = data.get('gallery_order', [])

            if avatar_id and str(avatar_id).startswith('gallery_image_'):
                g_id = int(str(avatar_id).replace('gallery_image_', ''))
                try:
                    g_img = ProductImage.objects.get(id=g_id, product=product)
                    old_avatar_file = product.image.name if product.image else None
                    if g_img.image:
                        product.image.name = g_img.image.name
                        product.save(update_fields=['image'])
                        if old_avatar_file:
                            g_img.image.name = old_avatar_file
                            g_img.save(update_fields=['image'])
                        else:
                            g_img.delete()
                except ProductImage.DoesNotExist:
                    pass

            for idx, g_pk in enumerate(gallery_order):
                ProductImage.objects.filter(pk=g_pk, product=product).update(order=idx)

            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        product = form.instance
        avatar_id = request.POST.get('selected_avatar_id')
        if avatar_id and str(avatar_id).startswith('gallery_image_'):
            try:
                g_id = int(str(avatar_id).replace('gallery_image_', ''))
                g_img = ProductImage.objects.get(id=g_id, product=product)
                old_avatar_file = product.image.name if product.image else None
                if g_img.image:
                    product.image.name = g_img.image.name
                    product.save(update_fields=['image'])
                    if old_avatar_file:
                        g_img.image.name = old_avatar_file
                        g_img.save(update_fields=['image'])
                    else:
                        g_img.delete()
            except Exception:
                pass



    def toggle_active(self, request, pk):
        from django.http import JsonResponse
        if request.method != 'POST' or not request.user.has_perm('main.change_product'):
            return JsonResponse({'ok': False}, status=403)
        product = Product.objects.get(pk=pk)
        product.is_active = not product.is_active
        product.save(update_fields=['is_active'])
        return JsonResponse({'ok': True, 'is_active': product.is_active})

    def update_order(self, request, pk):
        from django.http import JsonResponse
        if request.method != 'POST' or not request.user.has_perm('main.change_product'):
            return JsonResponse({'ok': False}, status=403)
        try:
            value = int(request.POST.get('order', 0))
        except (TypeError, ValueError):
            return JsonResponse({'ok': False}, status=400)
        product = Product.objects.get(pk=pk)
        product.order = value
        product.save(update_fields=['order'])
        return JsonResponse({'ok': True, 'order': product.order})

    def changelist_view(self, request, extra_context=None):
        if 'list_per_page' in request.GET:
            try:
                per_page = int(request.GET['list_per_page'])
                if per_page in (20, 50, 100):
                    self.list_per_page = per_page
            except (TypeError, ValueError):
                pass
            request.GET = request.GET.copy()
            del request.GET['list_per_page']
        extra_context = extra_context or {}
        current_category = request.GET.get('category__id__exact', '')
        categories = []
        for cat in ProductCategory.objects.all():
            categories.append({'obj': cat, 'count': Product.objects.filter(category=cat).count()})
        extra_context['product_categories'] = categories
        extra_context['total_count'] = Product.objects.count()
        extra_context['current_category'] = current_category
        extra_context['current_is_active'] = request.GET.get('is_active__exact', '')
        response = super().changelist_view(request, extra_context)
        cl = getattr(response, 'context_data', {}).get('cl')
        if cl is not None:
            page = cl.paginator.page(cl.page_num)
            response.context_data['range_start'] = page.start_index()
            response.context_data['range_end'] = page.end_index()
        return response


@admin.register(NewsCategory)
class NewsCategoryAdmin(ModelAdmin):
    change_list_template = 'admin/main/newscategory/change_list.html'
    list_fullwidth = True
    list_display = ['name', 'slug', 'news_count']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

    def news_count(self, obj):
        return obj.news_set.count()
    news_count.short_description = "Số lượng bài viết"

    def changelist_view(self, request, extra_context=None):
        if 'list_per_page' in request.GET:
            try:
                per_page = int(request.GET['list_per_page'])
                if per_page in (10, 20, 50, 100):
                    self.list_per_page = per_page
            except (TypeError, ValueError):
                pass
            request.GET = request.GET.copy()
            del request.GET['list_per_page']
        extra_context = extra_context or {}
        extra_context['total_count'] = NewsCategory.objects.count()
        response = super().changelist_view(request, extra_context)
        cl = getattr(response, 'context_data', {}).get('cl')
        if cl is not None:
            page = cl.paginator.page(cl.page_num)
            response.context_data['range_start'] = page.start_index()
            response.context_data['range_end'] = page.end_index()
        return response


@admin.register(Banner)
class BannerAdmin(ModelAdmin):
    list_display = ['title', 'order', 'is_active']
    list_editable = ['order', 'is_active']


@admin.register(Distributor)
class DistributorAdmin(ModelAdmin):
    list_display = ['name', 'province', 'phone', 'is_active']
    list_filter = ['province', 'is_active']
    list_editable = ['is_active']
    search_fields = ['name', 'province', 'phone']


@admin.register(DealerRegistration)
class DealerRegistrationAdmin(ModelAdmin):
    list_display = ['company', 'phone', 'tax_id', 'province', 'created_at', 'is_processed']
    list_filter = ['province', 'is_processed']
    list_editable = ['is_processed']
    search_fields = ['company', 'phone', 'tax_id']
    readonly_fields = ['created_at']


@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    list_display = ['full_name', 'phone', 'email', 'created_at', 'is_read']
    list_editable = ['is_read']
    readonly_fields = ['created_at']
    search_fields = ['full_name', 'phone']


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(ModelAdmin):
    change_list_template = 'admin/main/projectcategory/change_list.html'
    list_fullwidth = True
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

    def changelist_view(self, request, extra_context=None):
        if 'list_per_page' in request.GET:
            try:
                per_page = int(request.GET['list_per_page'])
                if per_page in (10, 20, 50, 100):
                    self.list_per_page = per_page
            except (TypeError, ValueError):
                pass
            request.GET = request.GET.copy()
            del request.GET['list_per_page']
        extra_context = extra_context or {}
        extra_context['total_count'] = ProjectCategory.objects.count()
        response = super().changelist_view(request, extra_context)
        cl = getattr(response, 'context_data', {}).get('cl')
        if cl is not None:
            page = cl.paginator.page(cl.page_num)
            response.context_data['range_start'] = page.start_index()
            response.context_data['range_end'] = page.end_index()
            for obj in cl.result_list:
                obj.count = Project.objects.filter(category=obj.slug).count()
        return response


@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    change_list_template = 'admin/main/project/change_list.html'
    change_form_template = 'admin/main/project/change_form.html'
    list_fullwidth = True
    list_display = ['title_with_image', 'category', 'author', 'is_active', 'published_at', 'updated_at']
    list_filter = ['category', 'author', 'is_active']
    search_fields = ['title', 'client', 'location']
    date_hierarchy = 'published_at'
    ordering = ['order', '-is_featured', '-created_at']
    fields = ['title', 'category', 'author', 'image', 'description']

    actions = ['bulk_edit_action']

    @admin.action(description='Chỉnh sửa các dự án đã chọn')
    def bulk_edit_action(self, request, queryset):
        from django.shortcuts import redirect
        from django.urls import reverse
        pks = ','.join(str(p.pk) for p in queryset)
        return redirect(f"{reverse('admin:main_project_bulk_edit')}?ids={pks}")

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('bulk-edit/', self.admin_site.admin_view(self.bulk_edit_view), name='main_project_bulk_edit'),
            path('toggle-active/<int:pk>/', self.admin_site.admin_view(self.toggle_active), name='main_project_toggle_active'),
            path('update-order/<int:pk>/', self.admin_site.admin_view(self.update_order), name='main_project_update_order'),
            path('reorder-projects/', self.admin_site.admin_view(self.reorder_projects), name='main_project_reorder_projects'),
        ]
        return custom_urls + urls

    def bulk_edit_view(self, request):
        from django.shortcuts import render, redirect
        from django.contrib import messages
        from .models import PROJECT_CATEGORY_CHOICES

        if not request.user.has_perm('main.change_project'):
            messages.error(request, 'Bạn không có quyền chỉnh sửa dự án.')
            return redirect('admin:main_project_changelist')

        if request.method == 'POST':
            pks = request.POST.getlist('project_ids')
            updated_count = 0
            for pk in pks:
                try:
                    project = Project.objects.get(pk=pk)
                    title = request.POST.get(f'title_{pk}')
                    category = request.POST.get(f'category_{pk}')
                    author = request.POST.get(f'author_{pk}')
                    client = request.POST.get(f'client_{pk}')
                    location = request.POST.get(f'location_{pk}')
                    is_active = request.POST.get(f'is_active_{pk}') == '1'

                    if title:
                        project.title = title.strip()
                    if category:
                        project.category = category.strip()
                    if author is not None:
                        project.author = author.strip()
                    if client is not None:
                        project.client = client.strip()
                    if location is not None:
                        project.location = location.strip()
                    project.is_active = is_active
                    project.save()
                    updated_count += 1
                except Project.DoesNotExist:
                    continue

            messages.success(request, f'Đã cập nhật thành công {updated_count} dự án.')
            return redirect('admin:main_project_changelist')

        ids_str = request.GET.get('ids', '')
        if ids_str:
            id_list = [int(x.strip()) for x in ids_str.split(',') if x.strip().isdigit()]
            projects = Project.objects.filter(id__in=id_list).order_by('order', 'id')
        else:
            projects = Project.objects.all().order_by('order', 'id')

        context = {
            **self.admin_site.each_context(request),
            'title': 'Chỉnh sửa nhiều dự án',
            'projects': projects,
            'categories': PROJECT_CATEGORY_CHOICES,
            'opts': self.model._meta,
        }
        return render(request, 'admin/main/project/bulk_edit.html', context)

    def toggle_active(self, request, pk):
        from django.http import JsonResponse
        if request.method != 'POST' or not request.user.has_perm('main.change_project'):
            return JsonResponse({'ok': False}, status=403)
        project = Project.objects.get(pk=pk)
        project.is_active = not project.is_active
        project.save(update_fields=['is_active'])
        return JsonResponse({'ok': True, 'is_active': project.is_active})

    def update_order(self, request, pk):
        from django.http import JsonResponse
        if request.method != 'POST' or not request.user.has_perm('main.change_project'):
            return JsonResponse({'ok': False}, status=403)
        try:
            value = int(request.POST.get('order', 0))
        except (TypeError, ValueError):
            return JsonResponse({'ok': False}, status=400)
        project = Project.objects.get(pk=pk)
        project.order = value
        project.save(update_fields=['order'])
        return JsonResponse({'ok': True, 'order': project.order})

    def reorder_projects(self, request):
        import json
        from django.http import JsonResponse
        if request.method != 'POST' or not request.user.has_perm('main.change_project'):
            return JsonResponse({'ok': False}, status=403)
        try:
            data = json.loads(request.body)
            pks = data.get('pks', [])
            start_order = int(data.get('start_order', 0))
            for i, pk in enumerate(pks):
                Project.objects.filter(pk=pk).update(order=start_order + i)
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)

    def changelist_view(self, request, extra_context=None):
        if 'list_per_page' in request.GET:
            try:
                per_page = int(request.GET['list_per_page'])
                if per_page in (10, 20, 50, 100):
                    self.list_per_page = per_page
            except (TypeError, ValueError):
                pass
            request.GET = request.GET.copy()
            del request.GET['list_per_page']
        extra_context = extra_context or {}
        current_category = request.GET.get('category__exact', '')
        
        # Build category list for tabs
        from .models import PROJECT_CATEGORY_CHOICES
        cat_map = dict(PROJECT_CATEGORY_CHOICES)
        try:
            for cat_obj in ProjectCategory.objects.all():
                cat_map[cat_obj.slug] = cat_obj.name
        except Exception:
            pass
            
        categories = []
        for slug, name in cat_map.items():
            count = Project.objects.filter(category=slug).count()
            categories.append({'slug': slug, 'name': name, 'count': count})
            
        extra_context['project_categories'] = categories
        extra_context['total_count'] = Project.objects.count()
        extra_context['current_category'] = current_category
        extra_context['current_is_active'] = request.GET.get('is_active__exact', '')
        response = super().changelist_view(request, extra_context)
        cl = getattr(response, 'context_data', {}).get('cl')
        if cl is not None:
            page = cl.paginator.page(cl.page_num)
            response.context_data['range_start'] = page.start_index()
            response.context_data['range_end'] = page.end_index()
        return response

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            try:
                cats = list(ProjectCategory.objects.all())
                if cats:
                    kwargs['widget'] = forms.Select(choices=[(c.slug, c.name) for c in cats])
            except Exception:
                pass
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    @admin.display(description='Tiêu đề')
    def title_with_image(self, obj):
        from django.utils.html import format_html
        style = "color: #007bff; font-size: 11px;"
        if obj.image:
            return format_html(
                '<div style="display: flex; align-items: center; gap: 10px;">'
                '<img src="{}" style="width: 40px; height: 30px; object-fit: cover; border-radius: 4px;" />'
                '<span style="{}">{}</span>'
                '</div>',
                obj.image.url, style, obj.title
            )
        return format_html('<span style="{}">{}</span>', style, obj.title)


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(ModelAdmin):
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
class CatalogueAdmin(ModelAdmin):
    list_display = ['title', 'category', 'group_name', 'order', 'created_at']
    list_filter = ['category', 'group_name']
    list_editable = ['group_name', 'order']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title']
    exclude = ['related_products', 'related_projects']


@admin.register(News)
class NewsAdmin(ModelAdmin):
    change_list_template = 'admin/main/news/change_list.html'
    list_fullwidth = True
    list_display = ['title_with_image', 'category', 'author', 'is_active', 'published_at', 'updated_at']
    list_filter = ['category', 'author', 'is_active']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'author']
    date_hierarchy = 'published_at'
    ordering = ['order', '-published_at']
    filter_horizontal = ['related_products', 'related_projects', 'related_articles']
    fieldsets = [
        (None, {'fields': ['title', 'slug', 'category', 'author', 'image', 'video_url', 'summary', 'content', 'order', 'published_at', 'is_active']}),
        ('Liên quan', {'fields': ['related_products', 'related_projects', 'related_articles'], 'classes': ['collapse']}),
    ]

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('toggle-active/<int:pk>/', self.admin_site.admin_view(self.toggle_active), name='main_news_toggle_active'),
            path('update-order/<int:pk>/', self.admin_site.admin_view(self.update_order), name='main_news_update_order'),
            path('reorder-news/', self.admin_site.admin_view(self.reorder_news), name='main_news_reorder_news'),
        ]
        return custom_urls + urls

    def toggle_active(self, request, pk):
        from django.http import JsonResponse
        if request.method != 'POST' or not request.user.has_perm('main.change_news'):
            return JsonResponse({'ok': False}, status=403)
        news = News.objects.get(pk=pk)
        news.is_active = not news.is_active
        news.save(update_fields=['is_active'])
        return JsonResponse({'ok': True, 'is_active': news.is_active})

    def update_order(self, request, pk):
        from django.http import JsonResponse
        if request.method != 'POST' or not request.user.has_perm('main.change_news'):
            return JsonResponse({'ok': False}, status=403)
        try:
            value = int(request.POST.get('order', 0))
        except (TypeError, ValueError):
            return JsonResponse({'ok': False}, status=400)
        news = News.objects.get(pk=pk)
        news.order = value
        news.save(update_fields=['order'])
        return JsonResponse({'ok': True, 'order': news.order})

    def reorder_news(self, request):
        import json
        from django.http import JsonResponse
        if request.method != 'POST' or not request.user.has_perm('main.change_news'):
            return JsonResponse({'ok': False}, status=403)
        try:
            data = json.loads(request.body)
            pks = data.get('pks', [])
            start_order = int(data.get('start_order', 0))
            for i, pk in enumerate(pks):
                News.objects.filter(pk=pk).update(order=start_order + i)
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)

    def changelist_view(self, request, extra_context=None):
        if 'list_per_page' in request.GET:
            try:
                per_page = int(request.GET['list_per_page'])
                if per_page in (10, 20, 50, 100):
                    self.list_per_page = per_page
            except (TypeError, ValueError):
                pass
            request.GET = request.GET.copy()
            del request.GET['list_per_page']
        extra_context = extra_context or {}
        current_category = request.GET.get('category__id__exact', '')
        cats = []
        for cat in NewsCategory.objects.all():
            cats.append({'obj': cat, 'count': News.objects.filter(category=cat).count()})
        extra_context['news_categories'] = cats
        extra_context['total_count'] = News.objects.count()
        extra_context['current_category'] = current_category
        extra_context['current_is_active'] = request.GET.get('is_active__exact', '')
        response = super().changelist_view(request, extra_context)
        cl = getattr(response, 'context_data', {}).get('cl')
        if cl is not None:
            page = cl.paginator.page(cl.page_num)
            response.context_data['range_start'] = page.start_index()
            response.context_data['range_end'] = page.end_index()
        return response

    @admin.display(description='Tiêu đề')
    def title_with_image(self, obj):
        from django.utils.html import format_html
        style = "color: #007bff; font-size: 11px;"
        if obj.image:
            return format_html(
                '<div style="display: flex; align-items: center; gap: 10px;">'
                '<img src="{}" style="width: 40px; height: 30px; object-fit: cover; border-radius: 4px;" />'
                '<span style="{}">{}</span>'
                '</div>',
                obj.image.url, style, obj.title
            )
        return format_html('<span style="{}">{}</span>', style, obj.title)


class HomeBannerInline(TabularInline):
    model = HomeBanner
    extra = 1

class PartnerInline(TabularInline):
    model = Partner
    extra = 1

@admin.register(ThemeSettings)
class ThemeSettingsAdmin(ModelAdmin):
    change_list_template = 'admin/main/themesettings/change_list.html'
    change_form_template = 'admin/main/themesettings/change_form.html'
    
    inlines = [HomeBannerInline, PartnerInline]

    fieldsets = (
        ('Header', {
            'fields': ('header_text', 'logo', 'show_megamenu', 'hotline_1', 'hotline_2', 'email', 'open_hours'),
            'classes': ('tab-header',),
        }),
        ('Module Giới thiệu', {
            'fields': ('show_intro', 'intro_title', 'intro_description', 'intro_youtube_url'),
            'classes': ('tab-intro',),
        }),
        ('Chân trang', {
            'fields': ('footer_address', 'footer_phone', 'footer_email', 'footer_facebook', 'footer_zalo', 'footer_youtube'),
            'classes': ('tab-footer',),
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
