#The structure of the code is maintained as sourcecode on github repo
import cv2,boto3
import json,math
from bs4 import BeautifulSoup
import moviepy.editor as mpe
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from mutagen.mp3 import MP3

source_img = Image.open("./main/download.png").convert("RGBA")
draw = ImageDraw.Draw(source_img)
width,height=source_img.size
size = (width,height)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('final_output.mp4', fourcc, 24, size) 
polly_client = boto3.Session(
                        aws_access_key_id="Access key",                     
            aws_secret_access_key="secret key",
            region_name='ap-south-1').client('polly')
def text_wrap(text, font, max_width):
    lines = []
    # If the width of the text is smaller than image width
    # we don't need to split it, just add it to the lines array
    # and return
    if font.getsize(text)[0] <= max_width:
        lines.append(text) 
    else:
        # split the line by spaces to get words
        words = text.split(' ')  
        i = 0
        # append every word to a line while its width is shorter than image width
        while i < len(words):
            line = ''         
            while i < len(words) and font.getsize(line + words[i])[0] <= max_width:                
                line = line + words[i] + " "
                i += 1
            if not line:
                line = words[i]
                i += 1
            # when the line gets longer than the max width do not append the word, 
            # add the line to the lines array
            lines.append(line)    
    return lines

    


font = ImageFont.truetype("arialbd.ttf",20)
res = polly_client.synthesize_speech(VoiceId='Raveena',
                        OutputFormat='mp3', 
                        Text = '<speak><break time="1s"/></speak>',TextType='ssml')
break1sec=res['AudioStream'].read()
#for counting total number of questions.
count=0
#parsing the data from json.
with open('que.json') as jsonfile:
    x=json.load(jsonfile)
    for y in x["sec_details"][0]["sec_questions"]:
        count+=1
#Question count
number=0
#main audiofile
file = open('speech.mp3', 'wb') 
with open('que.json') as jsonfile:
    question=json.load(jsonfile)
    sec_id=question["sec_details"][0]["sec_id"]
    for section in question["sec_details"][0]["sec_questions"]:
        number+=1
        text_o1=[]
        for z in section["que"]["1"]["q_option"]:
            soup=BeautifulSoup(z,"html5lib")
            text_o1.append(soup.getText())
            
        soup=BeautifulSoup(section["que"]["1"]["q_string"],"html5lib")
        text_q_l=soup.getText().split()
        text_q=""
        for s in text_q_l:
            text_q+=s+" "
        text_qnu="Q."+str(number)
        
        text_qno="QUESTION "+str(number)+"/"+str(count);
        with open('ans.json') as jsonfile1:
            answer=json.load(jsonfile1)
            ans1=[]
            ans1=answer[sec_id][section["qid"]]["1"][0]
            if(ans1[0]==1):
                ans=str(0)
            elif(ans1[1]==1):
                ans=str(1)
            elif(ans1[2]==1):
                ans=str(2)
            elif(ans1[3]==1):
                ans=str(3)
        source_img = Image.open("./main/download.png").convert("RGBA")
        draw = ImageDraw.Draw(source_img)
        #for getting maximum height and width of options text.
        h,w=0,0
        for i in range(4):
            if(font.getsize(text_o1[i])[0]>w):
                w=font.getsize(text_o1[i])[0]
        for i in range(4):
            if(font.getsize(text_o1[i])[1]>h):
                h=font.getsize(text_o1[i])[1]

        file1=open("question_speech.mp3",'wb')
        
        response = polly_client.synthesize_speech(VoiceId='Raveena',
                        OutputFormat='mp3', 
                        Text = '<speak>Question number '+str(number)+'<break time="1s"/></speak>',TextType='ssml')
        
        questionNo_speech=response['AudioStream'].read()
        file.write(questionNo_speech)
        file1.write(questionNo_speech)
        
        response = polly_client.synthesize_speech(VoiceId='Raveena',
                        OutputFormat='mp3', 
                        Text = '<speak>'+text_q+'<break time="1s"/></speak>',TextType='ssml')
        

        question_speech=response['AudioStream'].read()
        
        file1.write(question_speech)
        file.write(question_speech)
        file1.close()
        audio = MP3("question_speech.mp3")        
        question_time=audio.info.length
        #for syncrhonizing options speech with visual animations.
        file2=open("option_speech.mp3",'wb')

        for i in range(len(text_o1)):
            response = polly_client.synthesize_speech(VoiceId='Raveena',
                        OutputFormat='mp3', 
                        Text = '<speak>Option '+chr(65+i)+" "+text_o1[i]+'<break time="1s"/></speak>',TextType='ssml')
            questionOption_speech=response['AudioStream'].read()
            file.write(questionOption_speech)
            file2.write(questionOption_speech)

        file2.close()
        audio = MP3("option_speech.mp3")        
        option_time=audio.info.length
        option_time=option_time/4
    
        #for syncrhonizing answer speech with visual animations.
        file3=open("answer_speech.mp3",'wb')

        for i in range(6):
            file.write(break1sec)
        response = polly_client.synthesize_speech(VoiceId='Raveena',
                        OutputFormat='mp3', 
                        Text = '<speak>Times up the Correct answer is option'+chr(int(ans)+65)+" "+text_o1[int(ans)]+'<break time="1s"/></speak>',TextType='ssml')

        correctAns_speech=response['AudioStream'].read()
        file.write(correctAns_speech)
        file3.write(correctAns_speech)  
        file3.close()
        audio = MP3("answer_speech.mp3")        
        answer_time=round(audio.info.length)  

     
        #Drawing and creating videoframes.
        draw.text((width/2-50,20),text_qno,fill='rgb(255,165,0)',font=font);
        (x,y)=70,50
        draw.text((x-40, y), text_qnu, fill='rgb(255,255,255)', font=font)
        line_height = font.getsize('hg')[1]
        lines = text_wrap(text_q, font, width-90)
        for line in lines:
            draw.text((x+10, y), line, fill='rgb(255,255,255)', font=font)
            y = y + line_height
        source_img.save("file.png", "PNG")
        img = cv2.imread("file.png")
        for i in range(24*math.ceil(question_time)):
            out.write(img)
        print(text_o1)
        
        ans_1=(x+10, y+line_height)
        ans_2=(int(width/2+x+10), y+line_height)
        ans_3=(x+10, y+h+100)
        ans_4=(int(width/2+x+10), y+h+100)
        for i in range(1,24):
            button_size_1 = (((w+200)/24)*i, h+20)
            button_img_1=Image.open('./main/a.png').convert("RGBA")
            button_img_1.thumbnail(button_size_1)
            button_draw_1 = ImageDraw.Draw(button_img_1)
            button_draw_1.text((50, 10), text_o1[0], font=font)
            source_img.paste(button_img_1, ans_1)
            source_img.save("file.png", "PNG")
            img = cv2.imread("file.png")
            out.write(img)
        for i in range(round(24*option_time)-23):
            out.write(img)
        
        for i in range(1,24):
            button_size_1 = (((w+200)/24)*i, h+20)
            button_img_2=Image.open('./main/b.png').convert("RGBA")
            button_img_2.thumbnail(button_size_1)
            button_draw_2 = ImageDraw.Draw(button_img_2)
            button_draw_2.text((50, 10), text_o1[1], font=font)
            source_img.paste(button_img_2, ans_2)
            source_img.save("file.png", "PNG")
            img = cv2.imread("file.png")
            out.write(img)
        for i in range(round(24*option_time)-23):
            out.write(img)

        for i in range(1,24):
            button_size_1 = (((w+200)/24)*i, h+20)
            button_img_3=Image.open('./main/c.png').convert("RGBA")
            button_img_3.thumbnail(button_size_1)
            button_draw_3 = ImageDraw.Draw(button_img_3)
            button_draw_3.text((50, 10), text_o1[2], font=font)
            source_img.paste(button_img_3, ans_3)
            source_img.save("file.png", "PNG")
            img = cv2.imread("file.png")
            out.write(img)
        for i in range(round(24*option_time)-23):
            out.write(img)

        for i in range(1,24):
            button_size_1 = (((w+200)/24)*i, h+20)
            button_img_4=Image.open('./main/d.png').convert("RGBA")
            button_img_4.thumbnail(button_size_1)
            button_draw_4 = ImageDraw.Draw(button_img_4)
            button_draw_4.text((50, 10), text_o1[3], font=font)
            source_img.paste(button_img_4, ans_4)
            source_img.save("file.png", "PNG")
            img = cv2.imread("file.png")
            out.write(img)
        for i in range(round(24*option_time)-23):
            out.write(img)

        for i in range(6):
            timer_img=Image.open("./main/"+str(i)+'s.png').convert("RGBA")
            timer_img.thumbnail((50,50))
            source_img.paste(timer_img, (int(width/2), y+h+200))
            source_img.save("file.png", "PNG")
            img = cv2.imread("file.png")
            for i in range(24):
                out.write(img)
        tick=Image.open('./main/tick.png').convert("RGBA")
        tick.thumbnail((50,50))
        button_size_1 = (w+250, h+25)
        if(ans==str(0)):
            righta=Image.open('./main/righta.png').convert("RGBA")
            righta.thumbnail(button_size_1)
            right = ImageDraw.Draw(righta)
            right.text((50, 10), text_o1[0], font=font)
            source_img.paste(righta, ans_1)
            source_img.paste(tick, (x+190, y+line_height+10))
        if(ans==str(1)):
            rightb=Image.open('./main/rightb.png').convert("RGBA")
            rightb.thumbnail(button_size_1)
            right = ImageDraw.Draw(rightb)
            right.text((50, 10), text_o1[1], font=font)
            source_img.paste(rightb, ans_2)
            source_img.paste(tick, (int(width/2+x+10)+180, y+line_height+10))
        if(ans==str(2)):
            
            rightc=Image.open('./main/rightc.png').convert("RGBA")
            rightc.thumbnail(button_size_1)
            right = ImageDraw.Draw(rightc)
            right.text((50, 10), text_o1[2], font=font)
            source_img.paste(rightc, ans_3)
            source_img.paste(tick, (x+190, y+h+110))
        if(ans==str(3)):
    
            rightd=Image.open('./main/rightd.png').convert("RGBA")
            rightd.thumbnail(button_size_1)
            right = ImageDraw.Draw(rightd)
            right.text((50, 10), text_o1[3], font=font)
            source_img.paste(rightd, ans_4)
            source_img.paste(tick, (int(width/2+x+10)+180, y+h+110))


        timer_end_img=Image.open('./main/timeisup.png').convert("RGBA")
        timer_img.thumbnail((50,50))
        source_img.paste(timer_end_img, (int(width/2-100), y+h+200))

        
        source_img.save("file.png", "PNG")
        img = cv2.imread("file.png")
        #For syncing correct answer speech
        for i in range(24*answer_time):
                out.write(img)
        
out.release()
file.close()

my_clip = mpe.VideoFileClip('final_output.mp4')
audio_background = mpe.AudioFileClip('speech.mp3')
final_audio = mpe.CompositeAudioClip([audio_background])
my_clip.audio = final_audio
my_clip.write_videofile('new_final.mp4')
#final_clip = my_clip.set_audio(final_audio)

                        
                    
                    

