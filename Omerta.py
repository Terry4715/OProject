import random
import time
from datetime import datetime, timedelta
from omerta_functions import create_session, login, logout, get_rank_level, get_info, rank_up, steal_cars, offer_cars, garage_work, shoot_for_ks, reset_ks_list, whack_a_fool
from accounts import accounts

# cfm_total_price = 120000
# cfm_price_per_100 = 50
steal_car_count = 1
# 

while 1:

    random.shuffle(accounts)
    family_details = []

    for i, (username, password, character) in enumerate(accounts):
        session = create_session()
        if session:

            # Complete login form
            print(f"Account #{i + 1}")
            try:
                login(username, password, character)

                rank_progress = get_rank_level()

                # options - rank_up, steal_cars, offer_cars, garage_work, shoot_for_ks, rank_up_with_cfm
                # ranking_up = ['Esme2']
                garage_working = ['Moleone'] # 'Michael', 'Chester', 'Arthur', 'Alfie', 'Lizzie'
                # focus_on_ks = ['Arthur', 'Alfie', 'Chester', 'Moleone', 'Esme2', 'Lizzie', 'BonnieG']

                if character in ['Moleone']:
                    garage_work()
                else:
                    steal_cars(steal_car_count)
                    offer_cars(chop_shop="Moleone")
                # else:
                try:
                    whack_a_fool()
                except:
                    print("Issue with account")

                # when_done = shoot_for_ks()
                # if when_done == 47:
                #     break


                # if character in focus_on_ks:
                #     shoot_for_ks()
                #     # if when_done == 47:
                #     #     continue

                # elif character in ['Aberama', 'GretaJ']:
                #     # try:
                #     #     whack_a_fool()
                #     # except:
                #     #     print("Issue with trying to whack a fool")
                #     steal_cars(steal_car_count)
                #     offer_cars(chop_shop="Michael")

                # elif character in ['Polly', 'May']:
                #     # try:
                #     #     whack_a_fool()
                #     # except:
                #     #     print("Issue with trying to whack a fool")
                #     steal_cars(steal_car_count)
                #     offer_cars(chop_shop="Moleone")
                
                # elif character in ['Audrey', 'Linda']:
                #     # try:
                #     #     whack_a_fool()
                #     # except:
                #     #     print("Issue with trying to whack a fool")
                #     steal_cars(steal_car_count)
                #     offer_cars(chop_shop="Chester")

                # elif character in ['Goliath', 'Vincente']:
                #     steal_cars(steal_car_count)
                #     offer_cars(chop_shop="Arthur")
                # elif character in ['JeremiahJ', 'Grace']:
                #     steal_cars(steal_car_count)
                #     offer_cars(chop_shop="Alfie")
                # elif character in ['Jessie', 'Finn']:
                #     steal_cars(steal_car_count)
                #     offer_cars(chop_shop="Lizzie")
                
                # elif character in ['BonnieG']:
                #     steal_cars(4) 
                #     offer_cars(chop_shop="Donkey Kong")

                # elif character in ['Michael']:
                #     try:
                #         # whack_a_fool()
                #         garage_work()
                #     except:
                #         print("Issue with trying to whack a fool")
                
                # elif character in garage_working:
                #     garage_work()

                # else:
                #     print("DOING NOTHING WITH THE PROFILE")
                #     break
                    

                # # get info
                profile_info = get_info(character) # (character, rank, cash, ks, rank_progress)
                family_details.append(profile_info)
                
                logout()
                time.sleep(4)  # should stop remote handling error
                # if i == len(accounts) - 1:
                #     reset_ks_list()
            except:
                print("Session fucked...")
        
        else:
            print("Unable to create session...")

    # # family details
    for char, rnk, csh, ks, rnk_lvl in family_details:
        print(f"{char}|{rnk}|{csh}|{ks}|{rnk_lvl}")

    # # sleep function
    dtn = datetime.now()
    dt = datetime.now() + timedelta(minutes=20, hours=0)
    print(f"Sleeping for 21min @ {dtn.hour}:{dtn.minute} ({dtn.day}/{dtn.month}/{dtn.year})")
    reset_ks_list()
    while datetime.now() < dt:
        time.sleep(60)

# TO DOs
# build database so key data easily available without running script every time
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
