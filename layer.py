from yowsup.layers.interface                           import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities  import TextMessageProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities  import OutgoingReceiptProtocolEntity
from yowsup.layers.protocol_acks.protocolentities      import OutgoingAckProtocolEntity

import time
import datetime
import json
import unirest

current_score = ['0', '']

# Text Message to check
message = 'YO'

# World Cup series id for massap up
WORLDCUP_ID = '2223'

# Timer to update the score
SCORE_TIMER = 5

class EchoLayer(YowInterfaceLayer):

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):
        #send receipt otherwise we keep receiving the same message over and over

        if True:
            receipt = OutgoingReceiptProtocolEntity(messageProtocolEntity.getId(), messageProtocolEntity.getFrom())

            if messageProtocolEntity.getBody().lower() == message.lower() :
                response = self.GetCurrentScore()
            else :
                response = "Please send -YO- to get score."

            outgoingMessageProtocolEntity = TextMessageProtocolEntity(
                response,
                to = messageProtocolEntity.getFrom())

            self.toLower(receipt)
            self.toLower(outgoingMessageProtocolEntity)

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        ack = OutgoingAckProtocolEntity(entity.getId(), "receipt", "delivery")
        self.toLower(ack)

    def GetCurrentScore(self):

        # Get current time
        current_time = int(time.time())

        # Difference between last score and current time
        diff = (datetime.datetime.fromtimestamp(current_time) - datetime.datetime.fromtimestamp(int(current_score[0])))

        count = 1

        # if Diff is more then 5 second set new score to current score else send last score
        if diff.total_seconds() > SCORE_TIMER :

            current_score[0] = str(current_time)

            # These code snippets use an open-source library. http://unirest.io/python
            response = unirest.get("https://devru-live-cricket-scores-v1.p.mashape.com/livematches.php",
              headers={
                "X-Mashape-Key": "f76O8zuLRNmshHWZSIZ41xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", # use your X-Mashape-key
                "Accept": "application/json"
              }
            )

            data = json.dumps(response.body, separators=(',',':'))
            matches = json.loads(data)

            current_s = ''

            for match in matches :

                if match['srsid'] == WORLDCUP_ID :
                
                    if match['header']['mchState'] == 'inprogress' or match['header']['mchState'] == 'complete' :

                        bat_id = match['miniscore']['batteamid']
                        bowl_id = match['miniscore']['bowlteamid']

                        if match['team1']['id'] == bat_id :
                            bat_name = match['team1']['sName']
                            bowl_name = match['team2']['sName']
                        else :
                            bat_name = match['team2']['sName']
                            bowl_name = match['team1']['sName']

                        score_head = match['header']['mnum']

                        batting_score = str(bat_name) + ' ' + match['miniscore']['batteamscore'] + '(' + match['miniscore']['overs'] + ')'

                        summary = match['miniscore']['striker']['fullName'] + ' ' + match['miniscore']['striker']['runs'] + '(' + match['miniscore']['striker']['balls'] + ')' + ', ' + match['miniscore']['nonStriker']['fullName'] + ' ' + match['miniscore']['nonStriker']['runs'] + '(' + match['miniscore']['nonStriker']['balls'] + ')'

                        bowl_score = match['miniscore']['bowlteamscore'] + ' ' + str(bowl_name)

                        status = match['header']['status']

                        score = score_head + ': ' + batting_score + ' v ' + bowl_score + ', ' + summary + ', ' + status

                        current_s = current_s + score + '\n'

            current_score[1] = current_s

        # Create Text response
        text_response = current_score[1]

        #Return details
        return text_response





        
