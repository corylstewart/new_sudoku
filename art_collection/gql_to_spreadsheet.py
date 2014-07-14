import time
import gdata.spreadsheet.service
import gdata.docs.service
import  gdata.docs.client
import gdata.docs.data
from google.appengine.api import images
from EnhancedHandler import EnhancedHandler as EH
import art_collection_db as ACDB
from io import BytesIO
from users import secret


class GqlToSpreadsheet(EH.EnhancedHandler):

    def get(self):
        email = 'cory.demopage.email@gmail.com'
        password = secret.password
        spreadsheet_key = '1LZ8UsfIPYR3f0ErlYtyJCG6RC8JfKymCWHH1s_0w5aU'
        worksheet_id = 'od6'


        pieces = ACDB.ArtWork().get_by_user(self.user)

        #create the pulling client
        pull_client = gdata.docs.service.DocsService()
        pull_client.ClientLogin(email, password)
        documents_feed = pull_client.GetDocumentListFeed()
        docs = []
        for document_entry in documents_feed.entry:
            docs.append(document_entry.title.text)

        #create the pushing client
        push_client = gdata.docs.client.DocsClient(source='cory demo page')
        push_client.api_version = "3"
        push_client.ssl = True
        push_client.ClientLogin(email, password, push_client.source)  
        
        #create the spreadsheet client
        spr_client = gdata.spreadsheet.service.SpreadsheetsService()
        spr_client.email = email
        spr_client.password = password
        spr_client.source = 'Creating a spreadsheet for mailing'
        spr_client.ProgrammaticLogin()     


        for piece in pieces:
            #this section place files with a photo in the drive
            f_name = str(piece.key.id())#+'.jpg'  #got rid of the jpg tag so they are now docs
            if f_name not in docs:
                content_type = 'image/jpeg'
                #saves files as jpg but can't fnd them when i query for list of files
                '''photo = BytesIO(piece.scaled_photo)
                newResource = gdata.docs.data.Resource(title=f_name)
                media = gdata.data.MediaSource(file_handle=photo,
                                               content_type = content_type,
                                               content_length = int(len(str(piece.scaled_photo))),
                                               file_name = f_name)
                newDocument = push_client.CreateResource(newResource,
                                create_uri=gdata.docs.client.RESOURCE_UPLOAD_URI+'?convert=false',
                                 media=media)'''
                try:
                    photo = BytesIO(piece.scaled_photo)
                    newResource = gdata.docs.data.Resource(title=f_name)
                    media = gdata.data.MediaSource(file_handle=photo,
                                                   content_type = content_type,
                                                   content_length = int(len(str(piece.scaled_photo))),
                                                   file_name = f_name)
                    emptyDocument = push_client.CreateResource(newResource, media=media)
                except:
                    pass



        #this section deals with spreadsheet
        cells = spr_client.GetCellsFeed(spreadsheet_key, worksheet_id)
        batch_request = gdata.spreadsheet.SpreadsheetsCellsFeed()
        for i, entry in enumerate(cells.entry):
            entry.cell.inputValue = ''
            batch_request.AddUpdate(cells.entry[i])
        try:
            updated = spr_client.ExecuteBatch(batch_request, cells.GetBatchLink().href)
        except:
            pass


        headers = {'title':1, 'location':2, 'value':3, 'photo':4}
        for header in headers:
            try:
                entry = spr_client.UpdateCell(row=1, col=headers[header], inputValue=header, 
                                                    key=spreadsheet_key, wksht_id=worksheet_id)
            except:
                pass


        for i, piece in enumerate(pieces):
            dict = {}
            dict['title'] = piece.title
            dict['location'] = piece.location
            dict['value'] = str(piece.value)
            dict['photo'] = str('id: ' + str(piece.key.id()))
            try:
                entry = spr_client.InsertRow(dict, spreadsheet_key, worksheet_id)
            except:
                pass
            

        self.write('done')