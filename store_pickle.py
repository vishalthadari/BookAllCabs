import pickle
import os



def store_cred(source, fbid, cred):
    filename = os.path.join(source, str(fbid)+".pickle")
    with open(filename, 'wb') as handle:
        pickle.dump(cred, handle, protocol=pickle.HIGHEST_PROTOCOL)


def retrieve_cred(source, fbid):

    #filename = str(fbid)+".pickle"
    filename = os.path.join(source, str(fbid)+".pickle")
    try:
        with open(filename, 'rb') as handle:
            b = pickle.load(handle)
            return b
    except:
        return None


