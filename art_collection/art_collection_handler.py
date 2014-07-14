<<<<<<< HEAD
from EnhancedHandler import EnhancedHandler as EH
from my_email_classes import email_sender as EMS
import art_collection_db as ACDB
from google.appengine.ext import ndb
#from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images
import urllib
import time


class AddToDatabaseHandler(EH.EnhancedHandler):
    '''handles the requests for /artcollection/add_art'''

    def get(self):
        '''serves the empty add art template'''
        #self.arg_dict['upload_url'] = blobstore.create_upload_url('/upload')
        self.render('add_art_to_database.html', **self.arg_dict)

    def post(self):
        '''handles the post request from /artcollection/add_art'''

        self.has_error = False
        if self.request.get('save_btn'):
            self.arg_dict['piece_title'] = self.request.get('piece_title')
            self.arg_dict['piece_artist'] = self.request.get('piece_artist')
            self.arg_dict['piece_location'] = self.request.get('piece_location')
            self.arg_dict['piece_medium'] = self.request.get('piece_medium')
            self.arg_dict['piece_purchase_price'] = self.request.get('piece_purchase_price')
            self.arg_dict['piece_value'] = self.request.get('piece_value')
            self.arg_dict['piece_value_app'] = self.request.get('piece_value_app')
            self.arg_dict['piece_app'] = self.request.get('piece_app')
            upload_files = self.request.POST['file_to_upload']
            self.arg_dict['piece_description'] = self.request.get('piece_description')
            if self.arg_dict['piece_title'] == '':
                self.arg_dict['title_error'] = 'Please enter a Title'
                self.has_error = True
            art = ACDB.ArtWork()
            if art.title_exists(self.arg_dict['piece_title'], self.user):
                self.arg_dict['title_error'] = 'That title already exist.  Chose another title or edit that piece'
                self.has_error = True
            if self.arg_dict['piece_purchase_price']:
                try:
                    self.arg_dict['piece_purchase_price'] = float(self.arg_dict['piece_purchase_price'])
                except:
                    self.arg_dict['purchase_price_error'] = 'That is not a valid price'
            if self.arg_dict['piece_value']:
                try:
                    self.arg_dict['piece_value'] = float(self.arg_dict['piece_value'])
                except:
                    self.arg_dict['price_error'] = 'That is not a valid price'
                    self.has_error = True
            if not self.has_error:
                if self.arg_dict['piece_title']:
                    art.title = self.arg_dict['piece_title']
                if self.arg_dict['piece_artist']:
                    art.artist = self.arg_dict['piece_artist']
                if self.arg_dict['piece_location']:
                    art.location = self.arg_dict['piece_location']
                if self.arg_dict['piece_medium']:
                    art.medium = self.arg_dict['piece_medium']
                if self.arg_dict['piece_purchase_price']:
                    art.purchase_price = self.arg_dict['piece_purchase_price']
                if self.arg_dict['piece_value']:
                    art.value = self.arg_dict['piece_value']
                if self.arg_dict['piece_app']:
                    art.appraised_by = self.arg_dict['piece_app']
                if self.arg_dict['piece_value_app']:
                    art.app_or_est = self.arg_dict['piece_value_app']
                if self.arg_dict['piece_description']:
                    art.description = self.arg_dict['piece_description']
                try:
                    upload_files.value
                    art.photo = upload_files.value
                    art.clean_photo()
                    art.user = self.user
                    key = art.put()
                    if key:
                        EMS.AdminAlertEmail().send_new_picure_upload()      ###new line to send emails
                        #self.arg_dict['success_message'] = 'Your entry has been saved.  Clear form to enter another piece'
                        self.redirect('/edit/' + (str(key).split()[1][:-1]))   ###new redirect to edit page rather than back to add page
                    else:
                        self.arg_dict['success_message'] = 'There was an error please try again!'
                except:
                    self.arg_dict['file_error'] = 'Please Select a file'
            self.render('add_art_to_database.html', **self.arg_dict)


class ImgHandler(EH.EnhancedHandler):
    '''serves the photo of the requested resource'''
    def get(self, resource):
        resource = int(urllib.unquote(resource))
        art = ACDB.ArtWork().get_by_id(resource)
        self.response.headers['Content-Type'] = 'image/jpeg'
        self.response.out.write(art.photo)

class ScaledHandler(EH.EnhancedHandler):
    '''serves the scaled photo of the requested resource'''
    def get(self, resource):
        resource = int(urllib.unquote(resource))
        art = ACDB.ArtWork().get_by_id(resource)
        self.response.headers['Content-Type'] = 'image/jpeg'
        self.response.out.write(art.scaled_photo)

class ThumbHandler(EH.EnhancedHandler):
    '''serves the thumbnail photo of the requested resource'''
    def get(self, resource):
        resource = int(urllib.unquote(resource))
        art = ACDB.ArtWork().get_by_id(resource)
        self.response.headers['Content-Type'] = 'image/jpeg'
        self.response.out.write(art.thumb_nail)


class CollectionHandler(EH.EnhancedHandler):
    '''handles requests for /artcollection/collection'''

    def get(self):
        '''serves the users entire collection'''
        self.arg_dict['art_works'] = ACDB.ArtWork().query(ACDB.ArtWork.user==self.user)
        self.render('show_art.html', **self.arg_dict)

    def post(self):
        '''handle the post request and serves a filtered query based on the
        query parameters'''
        self.arg_dict['piece_location'] = self.request.get('piece_location')
        self.arg_dict['piece_medium'] = self.request.get('piece_medium')
        self.arg_dict['piece_sorting'] = self.request.get('piece_sorting')
        art = ACDB.ArtWork().collection_page_query(self.user, 
                                                 self.arg_dict['piece_location'],
                                                 self.arg_dict['piece_medium'],
                                                 self.arg_dict['piece_sorting'])
        self.arg_dict['art_works'] = art
        self.render('show_art.html', **self.arg_dict)


class PieceEditHandler(EH.EnhancedHandler):
    '''handles requests for  /edit/'''

    def get(self, resource):
        resource = int(urllib.unquote(resource))
        art = ACDB.ArtWork().get_by_id(resource)
        if self.user <> art.user:
            self.write("Users do not match")
            return
        self.arg_dict['work'] = art
        stuff_dict= {'piece_title' : art.title,
                     'piece_artist' : art.artist,
                    'piece_location' : art.location,
                    'piece_medium' : art.medium,
                    'piece_purchase_price' : art.purchase_price,
                    'piece_value' : art.value,
                    'piece_value_app' : art.app_or_est,
                    'piece_app' : art.appraised_by,
                    'piece_description' : art.description}
        for key,value in stuff_dict.items():
            if value:
                self.arg_dict[key] = value
            else:
                self.arg_dict[key] = ''
        self.render('add_art_to_database.html', **self.arg_dict)

    def post(self, resource):
        resource = int(urllib.unquote(resource))
        hidden_resource = int(self.request.get('hidden_key'))
        if resource <> hidden_resource:
            self.write("Keys don't match.")
            return
        art = ACDB.ArtWork().get_by_id(resource)
        if art.user <> self.user:
            self.write("Users do not match")
            return
        if self.request.get('piece_title'):
            art.title = self.request.get('piece_title')
        if self.request.get('piece_artist'):
            art.artist = self.request.get('piece_artist')
        if self.request.get('piece_location'):
            art.location = self.request.get('piece_location')
        if self.request.get('piece_medium'):
            art.medium = self.request.get('piece_medium')
        if self.request.get('piece_purchase_price'):
            try:
                art.purchase_price = float(self.request.get('piece_purchase_price'))
            except:
                pass
        if self.request.get('piece_value'):
            try:
                art.value = float(self.request.get('piece_value'))
            except:
                pass
        if self.request.get('piece_value_app'):
            art.app_or_est = self.request.get('piece_value_app')
        if self.request.get('piece_app'):
            art.appraisedd_by = self.request.get('piece_app')
        if self.request.get('piece_description'):
            art.description = self.request.get('piece_description')
        upload_files = self.request.POST['file_to_upload']
        try:
            upload_files.value
            art.photo = upload_files.value
            art.clean_photo()
        except:
            pass
        art.put()
=======
from EnhancedHandler import EnhancedHandler as EH
import art_collection_db as ACDB
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images
import urllib
import time


class AddToDatabaseHandler(EH.EnhancedHandler):
    def get(self):
        self.arg_dict['upload_url'] = blobstore.create_upload_url('/upload')
        self.render('add_art_to_database.html', **self.arg_dict)

    def post(self):
        self.has_error = False
        if self.request.get('save_btn'):
            self.arg_dict['piece_title'] = self.request.get('piece_title')
            self.arg_dict['piece_artist'] = self.request.get('piece_artist')
            self.arg_dict['piece_location'] = self.request.get('piece_location')
            self.arg_dict['piece_medium'] = self.request.get('piece_medium')
            self.arg_dict['piece_purchase_price'] = self.request.get('piece_purchase_price')
            self.arg_dict['piece_value'] = self.request.get('piece_value')
            self.arg_dict['piece_value_app'] = self.request.get('piece_value_app')
            self.arg_dict['piece_app'] = self.request.get('piece_app')
            upload_files = self.request.POST['file_to_upload']
            self.arg_dict['piece_description'] = self.request.get('piece_description')
            if self.arg_dict['piece_title'] == '':
                self.arg_dict['title_error'] = 'Please enter a Title'
                self.has_error = True
            art = ACDB.ArtWork()
            if art.title_exists(self.arg_dict['piece_title'], self.user):
                self.arg_dict['title_error'] = 'That title already exist.  Chose another title or edit that piece'
                self.has_error = True
            if self.arg_dict['piece_purchase_price']:
                try:
                    self.arg_dict['piece_purchase_price'] = float(self.arg_dict['piece_purchase_price'])
                except:
                    self.arg_dict['purchase_price_error'] = 'That is not a valid price'
            if self.arg_dict['piece_value']:
                try:
                    self.arg_dict['piece_value'] = float(self.arg_dict['piece_value'])
                except:
                    self.arg_dict['price_error'] = 'That is not a valid price'
                    self.has_error = True
            if not self.has_error:
                if self.arg_dict['piece_title']:
                    art.title = self.arg_dict['piece_title']
                if self.arg_dict['piece_artist']:
                    art.artist = self.arg_dict['piece_artist']
                if self.arg_dict['piece_location']:
                    art.location = self.arg_dict['piece_location']
                if self.arg_dict['piece_medium']:
                    art.medium = self.arg_dict['piece_medium']
                if self.arg_dict['piece_purchase_price']:
                    art.purchase_price = self.arg_dict['piece_purchase_price']
                if self.arg_dict['piece_value']:
                    art.value = self.arg_dict['piece_value']
                if self.arg_dict['piece_app']:
                    art.appraised_by = self.arg_dict['piece_app']
                if self.arg_dict['piece_value_app']:
                    art.app_or_est = self.arg_dict['piece_value_app']
                if self.arg_dict['piece_description']:
                    art.description = self.arg_dict['piece_description']
                try:
                    upload_files.value
                    art.photo = upload_files.value
                    art.clean_photo()
                    art.user = self.user
                    key = art.put()
                    if key:
                        #self.arg_dict['success_message'] = 'Your entry has been saved.  Clear form to enter another piece'
                        self.redirect('/edit/' + (str(key).split()[1][:-1]))
                    else:
                        self.arg_dict['success_message'] = 'There was an error please try again!'
                except:
                    self.arg_dict['file_error'] = 'Please Select a file'
            self.render('add_art_to_database.html', **self.arg_dict)


class ImgHandler(EH.EnhancedHandler):
    def get(self, resource):
        resource = int(urllib.unquote(resource))
        art = ACDB.ArtWork().get_by_id(resource)
        self.response.headers['Content-Type'] = 'image/jpeg'
        self.response.out.write(art.photo)

class ThumbHandler(EH.EnhancedHandler):
    def get(self, resource):
        resource = int(urllib.unquote(resource))
        art = ACDB.ArtWork().get_by_id(resource)
        self.response.headers['Content-Type'] = 'image/jpeg'
        self.response.out.write(art.thumb_nail)

class ScaledHandler(EH.EnhancedHandler):
    def get(self, resource):
        resource = int(urllib.unquote(resource))
        art = ACDB.ArtWork().get_by_id(resource)
        self.response.headers['Content-Type'] = 'image/jpeg'
        self.response.out.write(art.scaled_photo)

class CollectionHandler(EH.EnhancedHandler):
    def get(self):
        self.arg_dict['art_works'] = ACDB.ArtWork().query(ACDB.ArtWork.user==self.user)
        self.render('show_art.html', **self.arg_dict)

    def post(self):
        self.arg_dict['piece_location'] = self.request.get('piece_location')
        self.arg_dict['piece_medium'] = self.request.get('piece_medium')
        self.arg_dict['piece_sorting'] = self.request.get('piece_sorting')
        art = ACDB.ArtWork().collection_page_query(self.user, 
                                                 self.arg_dict['piece_location'],
                                                 self.arg_dict['piece_medium'],
                                                 self.arg_dict['piece_sorting'])
        self.arg_dict['art_works'] = art



        self.render('show_art.html', **self.arg_dict)


class PieceEditHandler(EH.EnhancedHandler):
    def get(self, resource):
        resource = int(urllib.unquote(resource))
        art = ACDB.ArtWork().get_by_id(resource)
        if self.user <> art.user:
            self.write("Users do not match")
            return
        self.arg_dict['work'] = art
        stuff_dict= {'piece_title' : art.title,
                     'piece_artist' : art.artist,
                    'piece_location' : art.location,
                    'piece_medium' : art.medium,
                    'piece_purchase_price' : art.purchase_price,
                    'piece_value' : art.value,
                    'piece_value_app' : art.app_or_est,
                    'piece_app' : art.appraised_by,
                    'piece_description' : art.description}
        for key,value in stuff_dict.items():
            if value:
                self.arg_dict[key] = value
            else:
                self.arg_dict[key] = ''
        self.render('add_art_to_database.html', **self.arg_dict)

    def post(self, resource):
        resource = int(urllib.unquote(resource))
        hidden_resource = int(self.request.get('hidden_key'))
        if resource <> hidden_resource:
            self.write("Keys don't match.")
            return
        art = ACDB.ArtWork().get_by_id(resource)
        if art.user <> self.user:
            self.write("Users do not match")
            return
        if self.request.get('piece_title'):
            art.title = self.request.get('piece_title')
        if self.request.get('piece_artist'):
            art.artist = self.request.get('piece_artist')
        if self.request.get('piece_location'):
            art.location = self.request.get('piece_location')
        if self.request.get('piece_medium'):
            art.medium = self.request.get('piece_medium')
        if self.request.get('piece_purchase_price'):
            try:
                art.purchase_price = float(self.request.get('piece_purchase_price'))
            except:
                pass
        if self.request.get('piece_value'):
            try:
                art.value = float(self.request.get('piece_value'))
            except:
                pass
        if self.request.get('piece_value_app'):
            art.app_or_est = self.request.get('piece_value_app')
        if self.request.get('piece_app'):
            art.appraisedd_by = self.request.get('piece_app')
        if self.request.get('piece_description'):
            art.description = self.request.get('piece_description')
        upload_files = self.request.POST['file_to_upload']
        try:
            upload_files.value
            art.photo = upload_files.value
            art.clean_photo()
        except:
            pass
        art.put()
>>>>>>> origin/master
        self.redirect('/edit/'+str(resource))