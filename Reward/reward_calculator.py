import datetime
import json
import math
import requests
import time

kURLSponsors = "https://nightmarket.firebaseio.com/sponsor.json"
kURLUsers = "https://nightmarket.firebaseio.com/iOS_users.json"

def GetRewardAmount(sponsor):
  """ Compute the reward amount based on sponsor config."""
  
  # Check balance and sponsor config.
  if sponsor['balanceBTC'] <= 0:
    print("The compaign is finished!")
    return
  if 'reward_mode' not in sponsor:
    print("Sponsor config error")
    return

  # Return award.
  award = None
  if sponsor['reward_mode'] == 'fixed':
    reward = sponsor['single_reward_amount']
  elif sponsor['reward_mode'] == 'shared':
    if 'user_pool' in sponsor:
      # TODO(hwchang): Check whether user has been in pool.
      reward = sponsor['single_reward_amount']/float(len(sponsor['user_pool']))
    else:
      reward = sponsor['single_reward_amount']
  elif sponsor['reward_mode'] == 'duration':
    if 'reward_amount_per_min' not in sponsor:
      print("No reward amount specified")
      return
    reward = sponsor['reward_amount_per_min']

  if reward and reward <= sponsor['balanceBTC']:
    return reward
  else:
    # Return None if the reward_mode is not available.
    return

if __name__ == '__main__':
  while True:
    print("Start reward run at time: %s"%str(datetime.datetime.now()))

    # Retrieve user data.
    response = requests.get(kURLUsers, data=None)
    users = response.json()

    # Retrieve sponsor data. Assume sponser can move too!
    response = requests.get(kURLSponsors, data=None)
    sponsors = response.json()

    # TODO(hwchang): Check time stamp
    for user_id, user in users.iteritems():
      # A user can be in the reward area of more than one sponser,
      # so we need to check all sponsors.
      for sponsor_id, sponsor in sponsors.iteritems():
        diff_lat = user['latitude'] -
                   sponsor['incentive']['location']['latitude']
        diff_long = user['longitude'] -
                    sponsor['incentive']['location']['longitude']
        if (math.sqrt((diff_lat*diff_lat)+(diff_long*diff_long))
            < sponsor['incentive']['location']['radius_m']):
          print("User:%s in the reward area of %s"%(user_id, sponsor_id))
          reward = GetRewardAmount(sponsor)
          if not reward:
            continue
          print("Gets award: %f"%(reward))

          if 'user_pool' not in sponsor:
            sponsor['user_pool'] = dict()
            sponsor['user_pool'][user_id] = 0

          if (sponsor['reward_mode'] == 'fixed' and
              (user_id not in sponsor['user_pool'])):
            sponsor['user_pool'][user_id] = reward
          elif sponsor['reward_mode'] == 'duration':
            if user_id in sponsor['user_pool']:
              sponsor['user_pool'][user_id] += reward
            else:
              sponsor['user_pool'][user_id] = reward
          elif sponsor['reward_mode'] == 'shared':
            if user_id in sponsor['user_pool']:
              sponsor['user_pool'][user_id] += reward
            else:
              sponsor['user_pool'][user_id] = reward
        else:
          if 'user_pool' in sponsor and user_id in sponsor['user_pool']:
            del sponsor['user_pool'][user_id]

    # Update user pool data
    for sponsor_id, sponsor in sponsors.iteritems():
      url = "https://nightmarket.firebaseio.com/sponsor/%s.json"%sponsor_id
      response = requests.patch(url, data=json.dumps(
          dict(user_pool=sponsor["user_pool"])))

    break
    # Wait for 60 seconds to the next run.
    time.sleep(60)
