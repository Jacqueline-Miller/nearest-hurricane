#note that to get my code to run I had to pip install the tropycal, shapely, and cartopy libraries

from tropycal import tracks
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
# I also needed to pip install geopy. It's used to convert addresses to latitude and longitude coordinates.
from geopy.geocoders import Nominatim

def get_google_maps_url(latitude, longitude):
    # Generates a google map url of the user's specified latitude and longitude coordinates.
    # Since I have already confirmed that the latitude and longitude are within the North Atlantic Basin in the location_info function, I will not include exceptions for impossible latitude or longitude numbers.
    print(f"https://www.google.com/maps?q={latitude},{longitude}")

def error_handeling(latitude, longitude, location_in_north_atlantic):
    # Definition of boundaries of North Atlantic Hurricane Basin Lat Long range: 0 degrees N (Equator), 60 degrees N, 98 degrees W (-98 degrees), 0 degrees longitude (the prime Meridian)
            # confirm range of lat and long is within the North Atlantic Hurricane Basin
            if (latitude < 0) or (latitude > 60):
                location_in_north_atlantic == False
                print("\nIt was not possible to convert the text entered into a location in the North Atlantic Basin. ")
            elif (longitude < -98) or (longitude > 0):
                location_in_north_atlantic == False
                print("\nIt was not possible to convert the text entered into a location in the North Atlantic Basin. ")
            else:
                print("Does the following google maps link show the location you intended to enter? ")
                get_google_maps_url(latitude, longitude)
                confirm_url_location = ""
                while confirm_url_location != "Yes" and confirm_url_location != "yes" and confirm_url_location != "y" and confirm_url_location != "No" and confirm_url_location != "no" and confirm_url_location != "n":
                    confirm_url_location = input("Please enter \"yes\" or \"no\": ")
                if confirm_url_location == "Yes" or confirm_url_location == "yes" or confirm_url_location == "y":
                    location_in_north_atlantic = True
                else:
                    print("\nFor the latitude and longitude to return your intended location, you may need to include more detail such as the state or provience name, or even a percise address. ")
            return location_in_north_atlantic

def location_info():
    # prompt user for location information about a location in the north atlantic basin
    print("\nThis program reports the tropical cyclone that has gotten closest to a given location out of storms that have gotten within 100 km of a location in the North Atlantic Hurricane Basin. (tropical systems include hurricanes, tropical storms, tropical depressions, etc.)")
    print("The North Atlantic Hurricane Basin stretches from the equater in the south to the southern tip of Greenland in the north and from the Mexican Coast in the West to the Prime Meridian in the East.")
    location = input("\nEnter the city and country (if relevant, include state or province) or address of a location in the North Atlantic Hurricane Basin: ")

    # error message if it is not possible to convert location information
    location_in_north_atlantic = False
    while location_in_north_atlantic == False:
        try:
            # convert/attempt to convert location information into geolocation
            loc = Nominatim(user_agent="GetLoc")
            getLocation = loc.geocode(location)
        # Exception so that entering places that don't exist won't make you need to rerun the program.
        except UnboundLocalError:
            location_in_north_atlantic == False
            getLocation = None
            print("\nIt was not possible to convert the text entered into latitude and longitude coordinates. ")
        # The following if statements check to see if locations that were successfully converted into latitude and longitude points are within the North Atlantic Basin.
        if getLocation != None:
            latitude = getLocation.latitude
            longitude = getLocation.longitude
            location_in_north_atlantic = error_handeling(latitude, longitude, location_in_north_atlantic)

        if location_in_north_atlantic == False:
            print("The North Atlantic Hurricane Basin stretches from the equater in the south to the southern tip of Greenland in the north and from the Mexican Coast in the West to the Prime Meridian in the East.")
            location = input("\nEnter a city or address that falls within the North Atlantic Hurricane Basin: ")
    # assign geolocation to list to access later since I access latitude and longit
    point = [latitude, longitude]
    #point = [40.7,-74.0]
    return point

def userPreferences():
    hurricanesOnly = ""
    while hurricanesOnly != "Yes" and hurricanesOnly != "yes" and hurricanesOnly != "y" and hurricanesOnly != "No" and hurricanesOnly != "no" and hurricanesOnly != "n":
                hurricanesOnly = input("\nWould you like to limit the search to only hurricanes, excluding information about tropical depressions and tropical storms? Enter \"yes\" or \"no\": ")
                if hurricanesOnly == "Yes" or hurricanesOnly == "yes" or hurricanesOnly == "y":
                    limitCycloneOutput = True
                else:
                    limitCycloneOutput = False
    generate_plot = ""
    while generate_plot != "Yes" and generate_plot != "yes" and generate_plot != "y" and generate_plot != "No" and generate_plot != "no" and generate_plot != "n":
        generate_plot = input("Would you like to generate a file containing a plot detailing the path of the tropical cyclone/hurricane that passed closest to the specified location? Enter \"yes\" or \"no\": ")
        if generate_plot == "Yes" or generate_plot == "yes" or generate_plot == "y":
             plot_yes_no = True
        else:
             plot_yes_no = False
    return limitCycloneOutput, plot_yes_no

def gatherData(point):
    limitCycloneOutput, plot_yes_no = userPreferences()
    # Inform the user that the output that automatically appears while running tropical to show it's runtime is about to appear on the screen since someone I showed the output to was confused by this.
    print("Information about retrieving tropical weather system related data and how long it took to retrieve that data will now appear on the screen. ")
    # create a TrackDataset object to store info about hurricanes from the North Atlantic Basin
    n_atlantic_basin = tracks.TrackDataset(basin='north_atlantic',include_btk=False)

    # retrieve storms with their nearest points within 100 km of the specified location. More info: https://tropycal.github.io/tropycal/examples/analogs.html
    #by default storms are sorted by intensity
    # if the user specified interest in all tropical cyclones regardless of intensity, then I will not specify a minimum sustained wind speed.
    if limitCycloneOutput == False:
        storm_dict = n_atlantic_basin.analogs_from_point((point),radius=100)
    # if the user specified interest in only hurricanes, I will specify a minimum sustained windspeed equivelent to a category 1 hurricane (65 kt)
    else:
          storm_dict = n_atlantic_basin.analogs_from_point((point),radius=100, thresh={'v_min':65})
    # sort storms by proximity to the specified location
    storm_dict_sorted = dict(sorted(storm_dict.items(), key=lambda item: item[1]))
    # create list of storm names from keys so I can more easily access storm names.
    storm_list = list(storm_dict_sorted.keys())

    # Making it so that the following code only runs if at least one storm passed within 100 km of the specified location to avoid error messages breaking the code.
    if storm_dict != {}:
        # The dictionary only stores the storm ID, but for user friendly reporting, I'll want to retrieve the name of the storm
        closest_storm_info = n_atlantic_basin.get_storm(storm_list[0])
        closest_storm_name = closest_storm_info.name
        # If the user specified they wanted to save a plot of the nearest storm to a file, the following code will create a file of the nearest specified storm track and save it as a file. Otherwise, no plot will be generated.
        if plot_yes_no == True:
            n_atlantic_basin.plot_storm(storm_list[0])
            plt.savefig(f"{closest_storm_name}_{storm_list[0]}.png", format = 'png', dpi=300)
    else:
         closest_storm_name = "No storm found"
    #Inform users data retrieval is complete.
    print("Tropical cyclone data retrieval complete. I will now report the data about the location you requested. ")

    return storm_dict_sorted, storm_list, limitCycloneOutput, closest_storm_name, plot_yes_no

def print_data_for_user(storm_dict_sorted, storm_list, limitCycloneOutput, closest_storm_name, plot_yes_no):
    if limitCycloneOutput == True:
          storm_type = "hurricane"
          storm_types = "hurricanes"
    else:
          storm_type = "tropical cyclone"
          storm_types = "tropical cyclones"

    # print information about the nearest storms for user if there was a storm that passed within 100 km of that location. Otherwise, print that there were no storms within 100 km.
    if len(storm_list) > 0:
        print(f"\nThe {storm_type} that passed closest to the specified location was {closest_storm_name} with a storm ID of {storm_list[0]}. The center of the storm was only {storm_dict_sorted[storm_list[0]]} km from that location at it's nearest approach!" )
        if plot_yes_no == True:
             print(f"Your {storm_type} storm track was saved to the file named {closest_storm_name}_{storm_list[0]}.png")
        print(f"{len(storm_dict_sorted)} total {storm_types} have passed within 100 km of that location. ")
    # Cover the scenario that there are no tropical systems that passed within 100 kms of that location.
    else:
        print(f"\nNo {storm_types} have ever passed within 100 km of the location you specified. Seems like a potentially hurricane free zone ;)")

def main():
    point = location_info()
    storm_dict_sorted, storm_list, limitCycloneOutput, closest_storm_name, plot_yes_no = gatherData(point)
    print_data_for_user(storm_dict_sorted, storm_list, limitCycloneOutput, closest_storm_name, plot_yes_no)

if __name__ == "__main__":
    main()
