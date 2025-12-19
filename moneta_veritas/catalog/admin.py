from django.contrib import admin
from .models import Category, Country, Material, Mint, Coin, Banknote

admin.site.empty_value_display = 'Не задано'

class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'is_published')
    list_editable = ('is_published',)
    list_filter = ('is_published', 'created_at', 'author')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'content', 'image')
        }),
        ('Авторство и публикация', {
            'fields': ('author', 'is_published')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class CoinInline(admin.TabularInline):
    model = Coin
    extra = 0


class BanknoteInline(admin.TabularInline):
    model = Banknote
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        CoinInline,
        BanknoteInline,
    )
    list_display = (
        'title',
        'coin_count',
        'banknote_count'
    )
    
    def coin_count(self, obj):
        return obj.coin_set.count()
    coin_count.short_description = 'Монеты'
    
    def banknote_count(self, obj):
        return obj.banknote_set.count()
    banknote_count.short_description = 'Банкноты'


class CoinAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'category',
        'country',
        'year',
        'denomination',
        'currency',
        'is_published',
        'is_on_main',
        'created_at'
    )
    list_editable = (
        'is_published',
        'is_on_main'
    )
    list_filter = ('category', 'country', 'year', 'author', 'is_published', 'is_on_main')
    search_fields = ('name', 'description', 'author__username')
    list_display_links = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'category', 'country', 'year', 'image')
        }),
        ('Характеристики монеты', {
            'fields': ('denomination', 'currency', 'material', 'weight', 'diameter', 'mint')
        }),
        ('Авторство и публикация', {
            'fields': ('author', 'is_published', 'is_on_main')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class BanknoteAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'category',
        'country',
        'year',
        'denomination',
        'currency',
        'is_published',
        'is_on_main',
        'created_at'
    )
    list_editable = (
        'is_published',
        'is_on_main'
    )
    list_filter = ('category', 'country', 'year', 'author', 'is_published', 'is_on_main')
    search_fields = ('name', 'description', 'author__username')
    list_display_links = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'category', 'country', 'year', 'image')
        }),
        ('Характеристики банкноты', {
            'fields': ('denomination', 'currency', 'serial_number', 'width', 'height')
        }),
        ('Авторство и публикация', {
            'fields': ('author', 'is_published', 'is_on_main')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )




admin.site.register(Category, CategoryAdmin)
admin.site.register(Country)
admin.site.register(Material)
admin.site.register(Mint)
admin.site.register(Coin, CoinAdmin)
admin.site.register(Banknote, BanknoteAdmin)