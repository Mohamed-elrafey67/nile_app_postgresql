from django.urls import path
from django.shortcuts import render
from . import views


def map_test(request):
    return render(request, 'violations/map_test.html')


urlpatterns = [
    # Pages
    path('',          views.map_view,        name='map'),
    path('login/',    views.login_view,       name='login'),
    path('logout/',   views.logout_view,      name='logout'),
    path('test/',     map_test,               name='map_test'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Map APIs
    path('api/violations/',               views.violations_api,        name='violations_api'),
    path('api/violations/pending/',       views.pending_api,           name='pending_violations'),
    path('api/violations/<int:pk>/',      views.violation_detail_api,  name='violation_detail'),
    path('api/violations/<int:pk>/edit/', views.edit_violation_api,    name='edit_violation'),
    path('api/violations/<int:pk>/approve/', views.approve_violation_api, name='approve_violation'),
    path('api/violations/<int:pk>/notes/', views.notes_api,            name='violation_notes'),
    path('api/violations/<int:pk>/images/', views.upload_image_api,   name='upload_image'),
    path('api/violations/<int:pk>/survey-map/', views.upload_survey_map_api, name='upload_survey_map'),
    path('api/violations/<int:pk>/survey-map/view/', views.serve_survey_map, name='serve_survey_map'),
    path('api/violations/geojson/',       views.violations_geojson_api, name='violations_geojson'),
    path('api/geo/<str:gov_pcode>/',      views.geo_gov_api,           name='geo_gov_api'),
    path('api/filter-options/',           views.filter_options_api,    name='filter_options_api'),
    path('api/govs-summary/',             views.govs_summary_api,      name='govs_summary_api'),

    # Shapefile Import
    path('api/shapefile/preview/',        views.shapefile_preview_api, name='shapefile_preview'),
    path('api/shapefile/import/',         views.shapefile_import_api,  name='shapefile_import'),

    # Usage Tracking — تتبع الاستغلال
    path('api/violations/<int:pk>/usages/',              views.usage_list_api,        name='usage_list'),
    path('api/violations/<int:pk>/usages/add/',          views.usage_add_api,         name='usage_add'),
    path('api/violations/<int:pk>/usages/<int:usage_id>/approve/', views.usage_approve_api, name='usage_approve'),
    path('api/violations/<int:pk>/usages/calculate/',          views.usage_calculate_preview, name='usage_calculate'),
    path('api/violations/<int:pk>/usages/covering-decisions/', views.covering_decisions_api,  name='covering_decisions'),
    path('api/usage-types/',                             views.usage_types_api,       name='usage_types'),
    path('api/violations/<int:pk>/usages/<int:usage_id>/print/', views.usage_print_single, name='usage_print_single'),
    path('api/violations/<int:pk>/usages/print-all/',    views.usage_print_all,       name='usage_print_all'),

    # Export
    path('api/export/excel/', views.export_excel_view, name='export_excel'),
    path('api/export/pdf/',   views.export_pdf_view,   name='export_pdf'),

    # Admin Dashboard APIs
    path('admin-dashboard/api/stats/',          views.admin_stats_api,      name='admin_stats'),
    path('admin-dashboard/api/users/',          views.admin_users_api,      name='admin_users'),
    path('admin-dashboard/api/users/<int:user_id>/', views.admin_users_api, name='admin_user_detail'),
    path('admin-dashboard/api/users/<int:user_id>/toggle/', views.admin_toggle_user_api, name='admin_toggle_user'),
    path('admin-dashboard/api/logs/',           views.admin_logs_api,       name='admin_logs'),
    path('admin-dashboard/api/logs/export/',    views.admin_logs_export,    name='admin_logs_export'),
    path('admin-dashboard/api/govs/',           views.admin_govs_api,       name='admin_govs'),
    # Admin: القرارات الوزارية
    path('api/decisions/',                      views.decisions_api,         name='decisions_api'),
    path('api/decisions/<int:pk>/upload-pdf/',  views.decision_upload_pdf,  name='decision_upload_pdf'),
    path('api/decisions/<int:pk>/import-excel/', views.import_decision_excel, name='import_decision_excel'),
    path('api/decisions/<int:pk>/usage-rates/', views.decision_usage_rates, name='decision_usage_rates'),
    path('api/chatbot/',                         views.chatbot_api,           name='chatbot'),
    path('api/export/presentation/', views.export_presentation_view, name='export_presentation'),
    path('api/satellite/search/',                 views.satellite_search_api,  name='satellite_search'),
    path('api/satellite/compare/',                views.satellite_compare_api, name='satellite_compare'),
    path('api/satellite/change/',                 views.satellite_change_api,  name='satellite_change'),
    path('api/satellite/report/<int:pk>/',        views.satellite_report_api,  name='satellite_report'),
    path('satellite/report/<int:pk>/',            views.satellite_report_html, name='satellite_report_html'),
]
