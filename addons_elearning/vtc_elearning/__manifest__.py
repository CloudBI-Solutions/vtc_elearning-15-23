{
    'name': "VTC Elearning",
    'version': "1.0.0",
    'author': "Sythil Tech",
    'category': "Tools",
    'summary': "Allows users to upload videos to your website",
    'license':'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/certificate_view.xml',
        'views/comment_view_inherit.xml',
        'views/slide_slide_view_inherit.xml',
        'views/quiz_view_inherit.xml',
        'views/lecturers_view.xml',
        'views/student_view.xml',
        'views/course_level.xml',
        'views/slide_channel_inherit.xml',
        'views/rating_system.xml',
        'views/menu_action.xml',
    ],
    'demo': [],
    'depends': [
        'website_slides',
        'openeducat_quiz',
        'base_unit_vn',
        'rating'
        'contacts',
    ],
    'images':[

    ],
    'installable': True,
}