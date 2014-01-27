#!/usr/bin/env python

#
# nightcoin vault
#

import math
import sys
import json
import requests
import nightcoinrpc
import time

if __name__ == '__main__':
    
    ## Nightcoin
    # rationale: nightmarket experience should be extended after visiting nightmarket.
    # Experience is something we all shared and can be exchanged. Nightmarket experience is an earned currency.
    # prototype location-driven PoS
    
    ## connect to ntc vault, so u'll need to run a local nightcoin daemon and replace with your own credentials.
    conn = nightcoinrpc.connect_to_remote(user='nightcoinrpc',password='Co4BYXhxjvPEmdpbD3whp4KWBUCCGWYsvw3dtuXSSLTE',host='localhost',port=12177,use_https=True)
    
    while (1):
        
        print "--------------------------------"
        print "updating vault data via firebase"
        
        
        ## get user account
        url = "https://nightmarket.firebaseio.com/iOS_users.json"
        response = requests.get(url, data=None)
        user = response.json
        
        for k in response.json:
            ## check if user has ntc address
            if "ntc_address" in user[k]:
            
                # check balance
                ntc_balance = conn.getreceivedbyaddress(user[k]["ntc_address"])
                print "%s wallet balance %s"%(k,ntc_balance)
                
                ### need to do the authentication right
                #from firebase_token_generator import create_token
                #SECRET = 'UHCboYT88vA4geUx9L6M2G5JQH0Gk7lIyCfGV1JL'
                #custom_data = {'auth_data': 'foo', 'other_auth_data': 'bar'}
                #options = {'admin': True}
                #token = create_token(SECRET, custom_data, options)
                
                # update balance
                url = "https://nightmarket.firebaseio.com/iOS_users/%s.json"%k
                response = requests.patch(url, data=json.dumps(dict(ntc_balance=float(ntc_balance))))
            
            else:
                ## generate new local address
                print "no ntc address found. prepare to patch with a new one"
                user[k]["ntc_address"] = conn.getnewaddress()
                print "user %s - ntc address: %s"%(k,user[k]["ntc_address"])

                url = "https://nightmarket.firebaseio.com/iOS_users/%s.json"%k
                response = requests.patch(url, data=json.dumps(dict(ntc_address=user[k]["ntc_address"])))
    
    
        ## get user account
        url = "https://nightmarket.firebaseio.com/sponsor.json"
        response = requests.get(url, data=None)
        sponsor = response.json
        
        ## distribute rewards
        for k in response.json:
            if "user_pool" in sponsor[k]:
                for uid in sponsor[k]["user_pool"].keys():
                    if "ntc_address" in user[uid]:
                        if (float(sponsor[k]["user_pool"][uid])>10): ## only distribute if reward > 10 NTC
                            print "address: %s - NTC %f"%(user[uid]["ntc_address"],float(sponsor[k]["user_pool"][uid]))
                            conn.sendtoaddress(user[uid]["ntc_address"],float(sponsor[k]["user_pool"][uid]),"from sponsor","sponsored message")

                            # reset balance
                            url = "https://nightmarket.firebaseio.com/sponsor/%s/user_pool/%s.json"%(k,uid)
                            response = requests.delete(url)

        #sys.exit(0)
        print "sleep for 60 sec"

        time.sleep(60)