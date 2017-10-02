import configparser
import os

class HTMLTags:

    DEFAULT_POST_CLASS       = '_8mlbc _vbtk2 _t5r8b'
    DEFAULT_INFO_CLASS       = '_bugdy'
    DEFAULT_NAME_CLASS       = '_79dar'
    DEFAULT_LINK_CLASS       = '_56pjv'
    DEFAULT_FOLLOWERS_CLASS  = '_4zhc5 notranslate _j7lfh'
    DEFAULT_FOLLOWINGS_CLASS = '_4zhc5 notranslate _j7lfh'

    DEFAULT_DESCR_CLASS      = '_nk46a'
    DEFAULT_ALL_INFO_CLASS   = '_es1du _rgrbt'
    DEFAULT_LIKES_DIV_CLASS  = '_iuf51 _oajsw'
    DEFAULT_LIKES_SPAN_CLASS = '_tf9x3'
    DEFAULT_DATE_TIME_CLASS  = '_379kp'
    DEFAULT_MORE_COMMENTS    = '_jpmen _8zx0v'
    DEFAULT_COMMENT_LI_CLASS = '_2nyld'
    DEFAULT_MARK_CLASS       = '_cj5pn'
    DEFAULT_PHOTO_CLASS      = '_ovg3g'
    DEFAULT_PHOTO_A_CLASS    = '_ofpcv'
    DEFAULT_USR_NAME_A_CLASS = '_4zhc5 notranslate _jozwt'

    def __init__(self, init_file):
        self.post_class       = self.DEFAULT_POST_CLASS
        self.info_class       = self.DEFAULT_INFO_CLASS
        self.name_class       = self.DEFAULT_NAME_CLASS
        self.link_class       = self.DEFAULT_LINK_CLASS
        self.followers_class  = self.DEFAULT_FOLLOWERS_CLASS
        self.followings_class = self.DEFAULT_FOLLOWINGS_CLASS

        self.descr_class      = self.DEFAULT_DESCR_CLASS
        self.all_info_class   = self.DEFAULT_ALL_INFO_CLASS
        self.likes_div_class  = self.DEFAULT_LIKES_DIV_CLASS
        self.likes_span_class = self.DEFAULT_LIKES_SPAN_CLASS
        self.date_time_class  = self.DEFAULT_DATE_TIME_CLASS
        self.more_comments    = self.DEFAULT_MORE_COMMENTS
        self.comment_li_class = self.DEFAULT_COMMENT_LI_CLASS
        self.mark_class       = self.DEFAULT_MARK_CLASS
        self.photo_class      = self.DEFAULT_PHOTO_CLASS
        self.photo_a_class    = self.DEFAULT_PHOTO_A_CLASS
        self.usr_name_a_class = self.DEFAULT_USR_NAME_A_CLASS

        if os.path.isfile(init_file):
            settings = configparser.ConfigParser()
            settings.set('Account', 'post_class',       self.post_class)
            settings.set('Account', 'info_class',       self.info_class)
            settings.set('Account', 'name_class',       self.name_class)
            settings.set('Account', 'link_class',       self.link_class)
            settings.set('Account', 'followers_class',  self.followers_class)
            settings.set('Account', 'followings_class', self.followings_class)

            settings.set('Post', 'descr_class',      self.descr_class)
            settings.set('Post', 'all_info_class',   self.all_info_class)
            settings.set('Post', 'likes_div_class',  self.likes_div_class)
            settings.set('Post', 'likes_span_class', self.likes_span_class)
            settings.set('Post', 'date_time_class',  self.date_time_class)
            settings.set('Post', 'more_comments',    self.more_comments)
            settings.set('Post', 'comment_li_class', self.comment_li_class)
            settings.set('Post', 'mark_class',       self.mark_class)
            settings.set('Post', 'photo_class',      self.photo_class)
            settings.set('Post', 'photo_a_class',    self.photo_a_class)
            settings.set('Post', 'usr_name_a_class', self.usr_name_a_class)

            settings.read(init_file)
            self.post_class       = settings.get('Account', 'post_class')
            self.info_class       = settings.get('Account', 'info_class')
            self.name_class       = settings.get('Account', 'name_class')
            self.link_class       = settings.get('Account', 'link_class')
            self.followers_class  = settings.get('Account', 'followers_class')
            self.followings_class = settings.get('Account', 'followings_class')

            self.descr_class      = settings.get('Post', 'descr_class')
            self.all_info_class   = settings.get('Post', 'all_info_class')
            self.likes_div_class  = settings.get('Post', 'likes_div_class')
            self.likes_span_class = settings.get('Post', 'likes_span_class')
            self.date_time_class  = settings.get('Post', 'date_time_class')
            self.more_comments    = settings.get('Post', 'more_comments')
            self.comment_li_class = settings.get('Post', 'comment_li_class')
            self.mark_class       = settings.get('Post', 'mark_class')
            self.photo_class      = settings.get('Post', 'photo_class')
            self.photo_a_class    = settings.get('Post', 'photo_a_class')
            self.usr_name_a_class = settings.get('Post', 'usr_name_a_class')
