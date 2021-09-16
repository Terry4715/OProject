import random
import time
from datetime import datetime, timedelta
from omerta_functions import create_session, login, logout, get_rank_level, get_info, rank_up, steal_cars, offer_cars, garage_work, shoot_for_ks, reset_ks_list
from dummy_accounts import accounts

# cfm_total_price = 120000
# cfm_price_per_100 = 50
steal_car_count = 6

while 1:

    random.shuffle(accounts)
    family_details = []

    for i, (username, password, character) in enumerate(accounts):
        session = create_session()
        if session:

            # Complete login form
            print(f"Account #{i + 1}")
            login(username, password, character)

            rank_progress = get_rank_level()

            # options - rank_up, steal_cars, offer_cars, garage_work, shoot_for_ks, rank_up_with_cfm
            ranking_up = ['Audrey', 'GretaJ', 'Aberama', 'Michael']
            garage_working = ['Moleone', 'Arthur', 'Alfie', 'Lizzie', 'Chester']

            if character in ranking_up:
                # rank_up_with_cfm(cfm_total_price, cfm_price_per_100)
                shoot_for_ks()
            elif character in ['Finn', 'Esme']:
                steal_cars(steal_car_count) 
                offer_cars(chop_shop="Moleone")
                shoot_for_ks()
            elif character in ['Polly', 'May']:
                steal_cars(steal_car_count) 
                offer_cars(chop_shop="Arthur")
                shoot_for_ks()
            elif character in ['Grace', 'Goliath']:
                steal_cars(steal_car_count) 
                offer_cars(chop_shop="Alfie")
                shoot_for_ks()
            elif character in ['Jessie', 'Vincente']:
                steal_cars(steal_car_count) 
                offer_cars(chop_shop="Lizzie")
                shoot_for_ks()
            elif character in ['JeremiahJ', 'Linda']:
                steal_cars(steal_car_count) 
                offer_cars(chop_shop="Chester")
                shoot_for_ks()
            elif character in ['BonnieG']:
                steal_cars(steal_car_count) 
                offer_cars(chop_shop="Donkey Kong")
                shoot_for_ks()
            elif character in garage_working:
                garage_work()
                shoot_for_ks()

            # # get info
            profile_info = get_info(character) # (character, rank, cash, ks, rank_progress)
            family_details.append(profile_info)
            
            logout()
            time.sleep(4)  # should stop remote handling error
            if i == len(accounts) - 1:
                reset_ks_list()

    # # family details
    for char, rnk, csh, ks, rnk_lvl in family_details:
        print(f"{char}|{rnk}|{csh}|{ks}|{rnk_lvl}")

    # # sleep function
    dtn = datetime.now()
    dt = datetime.now() + timedelta(minutes=20, hours=0)
    print(f"Sleeping for 21min @ {dtn.hour}:{dtn.minute} ({dtn.day}/{dtn.month}/{dtn.year})")
    while datetime.now() < dt:
        time.sleep(60)

# TO DOs
# create function that sends cash when needed
# create function to launder money
# create shoot_for_ks only function - if everyone hit stop shooting for 20mins
# update tools for stealing cars function as not working correctly
# review garage function as min cash requirement needed to accept offer as first step
# review all code for break potential
# potentially restructure code so that next steps dependant on return code after each function call
# create function to store legal cash from time to time
# review function and limit number of times keygen is brut forced
# create function to analyse any family

# https://www.omertamafia.com/war_success.php?dude=Everyone
