import hashlib

class InstaAccount:
    def __init__( self
                , insta_name
                , name
                , description
                , posts
                , followers=[]
                , followings=[]):
        self.insta_name = insta_name
        self.name = name
        self.description = description
        self.posts = posts
        self.followers = followers
        self.followings = followings


    def __str__(self):
        post_data = map(lambda index, post: '\t[{1}]: {2}'.format(index, str(post)), enumerate(self.posts))
        rel_links = ', '.join(self.description[1])
        fields = 'Id: {0}\nUser name: {1}\nDescription: {2}\nRelated links {3}\nPosts:' \
                    .format( self.insta_name
                           , self.name
                           , self.description[0]
                           , rel_links
                           , '\n'.join(post_data)
                           )
        return fields


    def index(self):
        return hashlib.sha224(self.insta_name.encode('utf-8')).hexdigest()
