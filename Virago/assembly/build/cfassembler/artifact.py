import os
import zipfile
import shutil

srcdir = os.environ['CODEBUILD_SRC_DIR']+"/src/"

def createDir():
    os.makedirs(srcdir+os.environ['branchname'],exist_ok=True)
    pass
def writeCfTemplate(templatejson):
    with open(srcdir+os.environ['branchname']+'/cftemplate-{}.json'.format(os.environ['branchname']),'w') as template:
        template.write(templatejson)
def createArtifact(entry,type):
    if(type=='lambda'):
        print("Adding ZIP: {} into artifact folder".format(entry['source']))
        zipf = zipfile.ZipFile(srcdir+os.environ['branchname']+"/"+entry['source']+".zip", 'w', zipfile.ZIP_DEFLATED)
        for root,dirs,files in os.walk(srcdir+"lambda/"+entry['source']+"/"):
            for f in files:
                base = srcdir+"lambda/"+entry['source']+"/"
                print(os.path.join(root,f))
                print(os.path.relpath(os.path.join(root,f),base))
                zipf.write(os.path.join(root,f),os.path.relpath(os.path.join(root,f),base))
        zipf.close()
    elif(type=='cloudformationtemplate'):
        shutil.copy(srcdir+"cloudformationtemplate/"+entry['source'],srcdir+os.environ['branchname']+"/"+entry['source'])
    
        
