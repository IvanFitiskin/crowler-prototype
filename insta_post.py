import hashlib

class InstaPost:
    def __init__( self
                , url
                , photo
                , descr
                , likes_count
                , date
                , comments
                , marks
                , photos_folder=None
                , photo_file=None):
        self.url           = url
        self.photo         = photo
        self.photo_file    = photo_file
        self.descr         = descr
        self.comments      = comments
        self.likes         = likes_count
        self.marks         = marks
        self.photos_folder = photos_folder
        self.date          = date


    def __str__(self):
        comments_repr = map(lambda index, comment: '\t{0}->Author: {1}\n\t\tText: {2}\n\t\tHashtags: {3}\n\t\tMarkes{4}\n'.\
                                   format( index
                                         , self.comment[0]
                                         , self.comment[1][0]
                                         , self.comment[1][2]
                                         , self.comments[i][1][1]),
                                   enumerate(self.comments))
        post_repr = 'Date: {0}\nPhoto: {1}\nDescr: {2}\nHashtags: {3}\nMarked: {4}\nLikes {5}\nComments: {6}\n'.\
                                    format( self.date
                                          , self.photo
                                          , self.descr[0]
                                          , self.descr[2]
                                          , self.descr[1]
                                          , self.likes
                                          , '\n'.join(comments_repr))
        return post_repr


    def index(self, account_name):
        return hashlib.sha224((account_name + self.url).encode('utf-8')).hexdigest()
