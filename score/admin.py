from django.contrib import admin
from django.utils.html import format_html
from .models import Score, ScoreFile


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'comp', 'arr', 'category', 'created_at')
    search_fields = ('title', 'comp', 'arr')
    list_filter = ('category',)
    ordering = ('title',)


@admin.register(ScoreFile)
class ScoreFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'score', 'file_preview', 'uploaded_at')
    list_filter = ('uploaded_at',)
    readonly_fields = ('file_preview',)

    def file_preview(self, obj):
        """Cloudinary上のファイルをプレビューまたはリンク表示"""
        if not obj.file_url:
            return "(ファイルなし)"

        url = obj.file_url

        # 画像ファイルならサムネイル表示
        if url.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            return format_html('<img src="{}" width="150" style="border:1px solid #ccc;"/>', url)
        # PDFならリンクで開く
        elif url.lower().endswith('.pdf'):
            return format_html('<a href="{}" target="_blank">PDFを開く</a>', url)
