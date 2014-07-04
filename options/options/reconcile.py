from options import make_blanks as mb
import datetime

class Reconcile:
    '''make sure that the position contains only the strikes that are listed
    in the option chain'''
    def reconcile_position(self, option_chain, position):
        for option in option_chain: #for options that are not in the position
            if option not in position: #add them
                position[option] = 0
        remove = []     #create an empty list for the options that need to bed removed
        for option in position:
            if option not in option_chain and option <> 'stock':
                remove.append(option)       #add names in the position that are not in the option chain
        for option in remove:
            position.pop(option, None)      #remove the options from the position
        return position

    def reconcile_vols(self, vols, expiry):
        'make sure the months in the vols are also the expirations of the stock'
        new_months = []     #create the empty list for months that are in expiry but not in vols
        for month in expiry:
            if month not in vols:
                new_months.append(month)        #add months to the list
        make_blank = mb.MakeBlanks()
        new_vols = make_blank.make_blank_vols(new_months)   #create a new month in the vols dictionary
        for month in new_vols:
            vols[month] = new_vols[month]       #add the new months that have been created to the vols
        remove = []         #create the empty list for months in vols but not in expiry
        for month in vols:
            if month not in expiry:
                remove.append(month)    #append list with months for in vols that are bad
        for month in remove:
            vols.pop(month, None)       #remove the months that are in the remove list
        return vols