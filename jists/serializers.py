from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import Jist, Topic, Vote
import requests
import re


class JistSerializer(serializers.ModelSerializer):
    poster_username = serializers.ReadOnlyField(source='poster.username')
    poster_id = serializers.ReadOnlyField(source='poster.id') 
    topic_id = serializers.ReadOnlyField(source='topic.id')
    votes = serializers.SerializerMethodField()

    class Meta:
        model = Jist
        fields = ['id', 'description', 'poster_username', 'poster_id', 'created', 'giphyUrl', 'votes', 'topic', 'topic_id']
        
    def get_votes(self, jist):
        return Vote.objects.filter(jist=jist).count()

class TopicSerializer(serializers.ModelSerializer):
    creator_username = serializers.ReadOnlyField(source='creator.username')
    creator_id = serializers.ReadOnlyField(source='creator.id')
    wikipedia_jist = serializers.SerializerMethodField()
    jists = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = ['id','name', 'created', 'jists', 'creator_id', 'creator_username', 'wikipedia_jist']

    def get_jists(self, topic):
        return Jist.objects.filter(topic=topic).values()
    
    def get_wikipedia_jist(request, self):
        # Converting Topic Name into URL-friendly format
        name = self.name
        new_url = name.split(" ")
        title = "_"
        title = title.join(new_url)

        # If topic name is too ambiguous (contains the phrase "may refer to"), find all alternatives in text retrieved from Wikipedia API
        # Then, create a string with the first 5 words found
        def find_similar_names(string):
            new_string = string.split("may refer to")
            string_two = new_string[1].split("==See also==")
            string_three = string_two[0]
            string_four = re.findall('\[\[.*?\]\]', string_three)
            similar_name = []
            for i in range(5):
                result = re.sub('[\[\]]+','', string_four[i])
                similar_name.extend([result])
            last = similar_name[-1]
            similar_name.pop()
            c = ", "
            c = c.join(similar_name)
            c = c + ", or " + last
            return c

        # GET Request to Wikipedia API
        response = requests.get("https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&origin=*&titles="+ title)
        dataresult = response.json()

        # Retreiving Page Number of Result (Wikipedia's API nests data within a unique page number. We need this value to get the data inside.)
        page_result = list(dataresult['query']['pages'].keys())[0]

        # -1 means -1 Page Number (i.e. unable to find results)
        if(page_result == '-1'):
            return "Wikipedia has no info on this topic.💔"
        # Split response into an array comprised of each sentence as an element
        listresult = dataresult['query']['pages'][page_result]['extract'].encode("utf-8").decode('ascii', 'ignore').split('.')

        # If topic name is ambiguous, prompt user to be more specific. Make a new request that grabs the options from Wikipedia's API
        if("may refer to" in str(listresult[0])):
            response = requests.get('https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvslots=*&rvprop=content&format=json&titles=' + title)
            ambiguous_data_result = response.json() 
            ambiguous_list_result = ambiguous_data_result['query']['pages'][page_result]['revisions'][0]['slots']['main']['*']
            list_of_alternatives = find_similar_names(ambiguous_list_result)
            return ValidationError("Please be more specific with your topic name. HINT: Try one of these topic names - " + list_of_alternatives)
        # Else if there are less than 3 sentences (but more than 0), return only the first sentence
        elif(len(listresult) < 3):
            return str(listresult[0]).encode("utf-8").decode("ascii", 'ignore')
        
        # Create a new array with the first three elements (sentences), join elements together, and return as a string to create a Jist from Wikipedia :)
        else:
            new_list = []
            new_list.extend([listresult[0], listresult[1], listresult[2]])
            p = "."
            p = p.join(new_list) + "."
            return str(p).encode("utf-8").decode('ascii', 'ignore')



class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id']
    