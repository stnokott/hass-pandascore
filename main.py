from custom_components.pandascore.sensor import APIManager

if __name__ == '__main__':
    apimanager = APIManager('Dj0B5iReMfiAR18SYd0D4fBgEI6792LAMkOsJqrc0JDQh0yu2UI', 'r6siege', 'G2')
    games = apimanager.get_upcoming_games(5)
    print(games)
