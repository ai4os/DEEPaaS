import argparse
import shutil
import ntpath
import os
import collections

from deepaas.model import loading
from oslo_log import log

LOG = log.getLogger(__name__)

### Loading the model installed 
def model_name():
    global MODEL_NAME
    try:
        for name, model in loading.get_available_models("v2").items():
            MODEL_NAME = name
    except Exception as e:
        LOG.warning("Error loading models: %s",e)



def main():
    model_name() #Function to know the name of the installed model

    package_name = MODEL_NAME
    predict_data=__import__(package_name).api.predict_data  #import function
    predict_url=__import__(package_name).api.predict_url  #import function

    parser = argparse.ArgumentParser (
            description= '''######Option to obtain the prediction of the model through the command line.##### ''',
            )
    parser.add_argument ("-ct", "--content_type", default="application/json" , help="Especify the content type of the file ('image/png', 'application/json', 'application/zip (by default application/json)')")
    parser.add_argument("input_file", help="Set input file to predict")
    parser.add_argument("-o", "--output", help="Save the result to a local file.", required=True)
    parser.add_argument("--url", type=bool, default=False, help="If we want to use the URL of an image as input method, we set this option to TRUE and use the image URL as input file.")
    args = parser.parse_args()
    output = args.output
    file_type = args.url

    UploadedFile = collections.namedtuple("UploadedFile", ("name",
                                                       "filename",
                                                       "content_type"))

    content_type = args.content_type
    
    file = UploadedFile(name=args.input_file, filename=args.input_file, content_type='image/png')

    

    if file_type == True:
        input_data = {'urls': [args.input_file], 'accept': content_type}
        output_pred = predict_url(input_data)
    else :
        input_data = {'files': [file], 'accept': content_type}
        output_pred = predict_data(input_data)

    dirName = output+"out_"+os.path.basename(args.input_file)+"_folder" 
    
    if content_type == 'image/png':
        output_path_image = output_pred.name       #Path where the resulting image is saved            
        if os.path.exists(dirName):
            shutil.rmtree(dirName)   ####if path already exists, remove it before copy with copytree()
        shutil.copytree(os.path.dirname(output_path_image),dirName)  #copy all files of output(image and json)
        print ("Image saved in: "+dirName )

    elif content_type == 'application/zip':
        if not os.path.exists(output):  ####if path does no exists, create it before copy
            os.makedirs(output)
        shutil.copyfile(output_pred.name,dirName+".zip")
        print ("Image saved in: "+dirName )
    elif content_type == 'application/json':
        f = open (os.path.basename(args.input_file)+".json","w+")
        f.write(repr(output_pred)+'\n')
        f.close()
        print (output_pred)
        if not os.path.exists(output):  ####if path does no exists, create it before copy
            os.makedirs(output)
        shutil.copy(f.name,output)
        os.remove(f.name)
    else:
        print ("Error in content_type")



if __name__ == "__main__":
    main()
