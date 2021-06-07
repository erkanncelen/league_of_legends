import requests
import riot_consts as consts
import riot_api_key as riot_api_key
import pandas as pd

ddragon_version = requests.get('https://ddragon.leagueoflegends.com/api/versions.json').json()[0]
ddragon_items = requests.get(('http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/item.json').format(version=ddragon_version)).json()
ddragon_champions = requests.get(('http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/championFull.json').format(version=ddragon_version)).json()

champions = pd.DataFrame.from_dict(ddragon_champions['data'], orient='index')
items = pd.DataFrame.from_dict(ddragon_items['data'], orient='index')




class riot_api(object):
    
# CORE
    def __init__(self, api_key=riot_api_key.KEY, region='TR'):
        self.api_key=api_key
        self.region=region
        
    def _request(self, api_url, params={}):
        args={'api_key': self.api_key}
        for key, value in params.items():
            if key not in args:
                args[key] = value
        response=requests.get(url=api_url, params=args)
        print(response.url)
        return response.json()


# SUMMONER ENDPOINT    
    def get_summoner_by_name(self, name):
        api_url=consts.URL['summoner_by_name'].format(
            region=consts.REGIONS[self.region],
            version=consts.API_VERSIONS['summoner'],
            name=name
        )
        return self._request(api_url)
    
    
# SPECTATOR ENDPOINT
    def get_current_game_by_summoner_name(self, name):
        summoner=self.get_summoner_by_name(name)
        api_url=consts.URL['current_game_by_summoner_name'].format(
            region=consts.REGIONS[self.region],
            version=consts.API_VERSIONS['spectator'],
            id=summoner['id']
        )
        
        return self._request(api_url)


# MATCH ENDPOINT
    def get_matches_by_summoner_name(self, name):
        summoner=self.get_summoner_by_name(name)
        
        api_url=consts.URL['matches_by_summoner_name'].format(
            proxy=consts.PROXIES[self.region],
            version=consts.API_VERSIONS['match'],
            puuid=summoner['puuid']
        ) 
        return self._request(api_url)
    
    def get_game_timeline_by_match_id(self, match_id):
        api_url=consts.URL['game_timeline_by_match_id'].format(
            proxy=consts.PROXIES[self.region],
            version=consts.API_VERSIONS['match'],
            match_id=match_id
        )
        return self._request(api_url)
            
    def get_match_info_by_match_id(self, match_id):
        api_url=consts.URL['match_info_by_match_id'].format(
            proxy=consts.PROXIES[self.region],
            version=consts.API_VERSIONS['match'],
            match_id=match_id
        )    
        return self._request(api_url)


# LEAGUE ENDPOINT
    def get_all_league_entries_by_queue_tier_division(self, queue='RANKED_SOLO_5x5', tier='PLATINUM', division='IV'):
        api_url=consts.URL['all_league_entries_by_queue_tier_division'].format(
            region=consts.REGIONS[self.region],
            version=consts.API_VERSIONS['league'],
            queue=queue,
            tier=tier,
            division=division)
        return self._request(api_url)
    
    def get_league_entries_by_summoner_id(self, summoner_id):
        api_url=consts.URL['league_entries_by_summoner_id'].format(
            region=consts.REGIONS[self.region],
            version=consts.API_VERSIONS['league'],
            encryptedSummonerId=summoner_id)
        return self._request(api_url)

    
# CHAMPION MASTERY ENDPOINT
    def get_champion_mastery_by_summoner_id_champion_id(self, summoner_id, champion_id):
        api_url=consts.URL['champion_mastery_by_summoner_id_champion_id'].format(
            region=consts.REGIONS[self.region],
            version=consts.API_VERSIONS['champion-mastery'],
            encryptedSummonerId=summoner_id,
            championId=champion_id)
        return self._request(api_url)
    
    def get_champion_masteries_by_summoner_id(self, summoner_id):
        api_url=consts.URL['champion_masteries_by_summoner_id'].format(
            region=consts.REGIONS[self.region],
            version=consts.API_VERSIONS['champion-mastery'],
            encryptedSummonerId=summoner_id)
        return self._request(api_url)
    
    def get_total_mastery_score_by_summoner_id(self, summoner_id):
        api_url=consts.URL['total_mastery_score_by_summoner_id'].format(
            region=consts.REGIONS[self.region],
            version=consts.API_VERSIONS['champion-mastery'],
            encryptedSummonerId=summoner_id)
        return self._request(api_url)
    
#TO DATAFRAME  
def game_to_df(game):
    columns = pd.DataFrame.from_dict(game['info']['participants'][0]).set_index('participantId').columns
    df = pd.DataFrame(columns=columns)
    for item in game['info']['participants']:
        temp = pd.DataFrame.from_dict(item).set_index('participantId')[:1]
        df = pd.concat([df, temp])
    return df

def performance_metrics(game):
    df = game_to_df(game)

    df['kda'] = (df['kills'] + df['assists'])/df['deaths']

    kills =  df[['championName', 'kills']].sort_values('kills', ascending=False)

    assists =  df[['championName', 'assists']].sort_values('assists', ascending=False)

    deaths = df[['championName', 'deaths']].sort_values('deaths', ascending=False)

    skills = df[['championName', 'spell1Casts', 'spell2Casts', 'spell3Casts', 'spell4Casts']]

    damage_magic = df[['championName', 'magicDamageDealtToChampions']].sort_values('magicDamageDealtToChampions', ascending=False)

    damage_physical = df[['championName', 'physicalDamageDealtToChampions']].sort_values('physicalDamageDealtToChampions', ascending=False)

    damage_true = df[['championName', 'trueDamageDealtToChampions']].sort_values('trueDamageDealtToChampions', ascending=False)

    damage_taken = df[['championName', 'totalDamageTaken']].sort_values('totalDamageTaken', ascending=False)

    kda = df[['championName', 'kda']].sort_values('kda', ascending=False)

    return kills, assists, deaths, skills, damage_magic, damage_physical, damage_true, damage_taken

