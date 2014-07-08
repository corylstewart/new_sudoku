from google.appengine.ext import ndb
from google.appengine.api import images
import sys


class ArtWork(ndb.Model):
    appraised_by = ndb.StringProperty()
    app_or_est = ndb.StringProperty()
    artist = ndb.StringProperty()
    description = ndb.TextProperty()
    location = ndb.StringProperty()
    medium = ndb.StringProperty()
    photo = ndb.BlobProperty()
    purchase_price = ndb.FloatProperty()
    scaled_photo = ndb.BlobProperty()
    title = ndb.StringProperty(required=True)
    thumb_nail = ndb.BlobProperty()
    user = ndb.StringProperty(required=True)
    value = ndb.FloatProperty()
    created = ndb.DateTimeProperty(auto_now_add = True)

    def title_exists(self, title, user):
        art = ArtWork().query(ArtWork.title == title,
                              ArtWork.user == user)
        if art.count() == 0:
            return False
        return True

    def retrieve_art(self, user, limit=50):
        art = ArtWork()
        return art.query(ArtWork.user == user).count(limit=limit)

    def clean_photo(self):
        img = images.Image(image_data = self.photo)
        img.im_feeling_lucky()        
        self.photo = img.execute_transforms(output_encoding=images.JPEG)
        while sys.getsizeof(self.photo) > 500000:
            img.resize(width=int(.9 * img.width))
            self.photo = img.execute_transforms(output_encoding=images.JPEG)
        img.resize(width=500,height=667)
        self.scaled_photo = img.execute_transforms(output_encoding=images.JPEG)
        img.resize(width=200,height=200)
        self.thumb_nail = img.execute_transforms(output_encoding=images.JPEG)

    def collection_page_query(self, user, location, medium, sorted_by):
        sort_map = {'Artist' : ArtWork.artist,
                         'Created' : ArtWork.created,
                         'Created Reverse' : -ArtWork.created, 
                         'Location' : ArtWork.location,
                         'Title' : ArtWork.title,
                         'Value' : ArtWork.value,
                         'Value Reverse' : -ArtWork.value}
        art = ArtWork().query(ArtWork.user==user)
        if location <> 'All':
            art = art.filter(ArtWork.location == location)
        if medium <> 'All':
            art = art.filter(ArtWork.medium == medium)
        if sorted_by <> 'None':
            art = art.order(sort_map[sorted_by])
            
        return art