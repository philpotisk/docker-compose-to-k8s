#!/usr/bin/python

import sys
import os
import getopt
import yaml

def addDeployment(containerName, deploymentFile, outputdir):
   fout = open(outputdir + '/' + 'deploy.sh', "a+")
   fout.write('kubectl -n uni-resolver delete -f %s \n'%deploymentFile)
   fout.write('kubectl -n uni-resolver create -f %s \n'%deploymentFile)
   fout.close()

def generateDeploymentSpecs(containterTags, outputdir):
    if os.path.exists(outputdir + '/' + 'deploy.sh'):
       os.remove(outputdir + '/' +'deploy.sh')
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)

    for containterTag in containterTags.split(';'):
        if (containterTag.find('/') < 0):
            return
        user,containerNameVersion = containterTag.split('/')
        containerName, containerVersion = containerNameVersion.split(':')
        fin = open("k8s-template.yaml", "rt")
        deploymentFile = "deployment-%s.yaml" % containerName
        fout = open(outputdir + '/' + deploymentFile, "wt")
        print('Writing file: ' + outputdir + '/' + deploymentFile + ' for containter: ' + containterTag)
        for line in fin:
            fout.write(line.replace('{containerName}', containerName).replace('{containterTag}', containterTag))
        addDeployment(containerName, deploymentFile, outputdir)
        fin.close()
        fout.close()

def findInDir(key, dictionary):
    for k, v in dictionary.items():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in findInDir(key, v):
                yield result

def getContainerTags(fileName):
    with open(fileName, 'r') as file:
        yaml_str = file.read()
        data = yaml.safe_load(yaml_str)

    containerTags = ''
    for x in findInDir("image", data):
        containerTags += x + ';'

    return containerTags

def main(argv):
   compose = 'docker-compose.yml'
   outputdir = './'
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["compose=","outputdir="])
   except getopt.GetoptError:
      print('convert.py -i <inputfile> -o <outputdir>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print ('convert.py -i <inputfile> -o <outputdir>')
         sys.exit()
      elif opt in ("-i", "--compose"):
         compose = arg
      elif opt in ("-o", "--outputdir"):
         outputdir = arg

   print ('Input file is:', compose)
   print ('Output dir is:', outputdir)

   containerTags = getContainerTags(compose)
   print("Container tags: " + containerTags)

   generateDeploymentSpecs(containerTags, outputdir)



if __name__ == "__main__":
   main(sys.argv[1:])