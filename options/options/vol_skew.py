import datetime

#this class currently does nothing other than set a flat vol skew across the expirations and the strikes
class VolSkew:
    def make_vol_skew(self, expiration_vols, option_chain):
        vols = {}
        for option in option_chain:
            skew = expiration_vols[option_chain[option]['expiry_string']]['skew']
            smile = expiration_vols[option_chain[option]['expiry_string']]['smile']
            vol = expiration_vols[option_chain[option]['expiry_string']]['vol']
            #do something here eventually
            vols[option] = vol
        return vols