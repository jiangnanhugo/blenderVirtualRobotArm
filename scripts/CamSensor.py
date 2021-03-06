#############################################################
#Author: Benoit CASTETS
#Date:19/05/2018
#Contents: Definition of camera sensor object
#############################################################

#############################################################
#LIBRARIES
#############################################################

#External libraries
###################

#numpy: library for array manipulation and mathematics
#imageio: library to read and write image
from blenderLibImport import *
import bge

#Custom Libraries
#################
import geoTools as gt
import imgProcess as ipros
import convertTools


#############################################################
#CLASS
#############################################################

class CamSensor():
    """
    """
    def __init__(self,blenderCamera):
        """Create a camera sensor
        
        Parameters:
        ----------
        blenderCamera:
            Blender camera object
        
        """
        #Blender camera used to capture image
        self.cam=blenderCamera
        #Width of the image generated by blender camera
        self.width=101
        #Height of the image generated by blender camera
        self.height=101
        #Image generated by blender camera
        self.image=None
        #Plane on which the camera is looking for object.
        #self.workPlane=None
    
    def redDetect(self):
        """Return True if red is detected by the camera with mass center location
        """
        pass
    def getImage(self):
        """Get camera image as numpy array
        """
        #https://blender.stackexchange.com/questions/88459/capture-video-from-cameras-in-blender-game-engine-for-artificial-intelligence?rq=1
        
        #https://blender.stackexchange.com/questions/88459/capture-video-from-cameras-in-blender-game-engine-for-artificial-intelligence?rq=1
        
        
        source = bge.texture.ImageRender(self.cam.scene,self.cam) 
        
        #Need to have a viewer port larger than 101x101
        #!! Need to check capsize order [width,height] or [height,width] 
        source.capsize=[self.width,self.height]

        imageArray = bge.texture.imageToArray(source, 'RGB') 

        image = np.array(imageArray.to_list())
        image=image.reshape(self.height,self.width,3)
        image=image.astype(np.uint8)
        
        #filePath="/media/bcastets/data/racine/Loisir/wordPress/articles/cobot/illustration/blender/render/gameImage.png"
        #scipy.misc.imsave(filePath,image)
        
        self.image=image
    def saveImage(self,filePath):
        """Take a picture with head camera and save it as a file
        """
        #print("Save head camera view in file")
        self.getImage()
        imageio.imwrite(filePath,self.image)
    
    def redDetect(self):
        """Return red mass center location in image. Return None if no red.
        
        Output
        ******
        location:
            ndArray (n,p) with n,p being the coordinate of red mass center
        """
        pxLocation=None
        self.getImage()
        img=self.image
        #Convert to HSV
        imgHsv=ipros.rgbToHsv(img)

        #Detect red
        #reminder: hue is between 0 and 182
        redMask=(s>30)*np.logical_or((h<10),(h>172))
        
        
        #print("center max position")
        #print(np.argmax(np.sum(redMask,1)))
        #print(np.argmax(np.sum(redMask,0)))
        
        #print(np.sum(redMask))
        if np.sum(redMask)==0:
            pxLocation=None
        else:
            massCenter=ndimage.measurements.center_of_mass(redMask*1)
            #print("mass center :",massCenter)
            pxLocation=np.array([massCenter[0],massCenter[1]])
            pxLocation=direction.astype(np.int)
        return pxLocation

    def pixelWorkSpaceLocation(pxLocation):
        """Return position of the projection of a pixel
        on the working plan in robot base referential.

        Parameters:
        ***********
        pxLocation:
            npArray with pixel coordinates [n.p]

        Return
        ******
        workSpaceLocation:
            Position on pixel projection on the workspace in robot base referential
            Expressed in blender unit.

        We make the assumption that:
        1/the camera is pointing down, is parallel and with a distance of 6 unit form the working plan
        2/Image p axis is same as robot base X axis
        3/Image n axis is same as robot base Y axis
        4/Camera resolution is 101*101px with a field of view of 65.2deg

        This is quite strong assumption. This will be changed in future versions.
        """
        #We calculate the surface of the working plane covered by the camera
        #And calculate the equivalent of one pixel in blender unit
        #This is not really accurate but we will work with this approximation

        #L: side of the squared region covered by the camera
        #H: Distance between the camera and the working space
        #Alpha: camera field of view
        #L=2*H*tan(Alpha/2)=2*6*tan(65.2/2)=7.674 Blender Unit
        
        #One pixel is equivalent to L/101=0.07674 Blender Unit

        camBlenderLocation=self.cam.location
        camNpLocation=convertTools.blenderToNp(camBlenderLocation)

        workSpaceLocation=np.array([0,0,0])

        #Position of the pixel from camera center in X,Y plan
        xPx=-51+pxLocation[1] 
        yPx=51-pxLocation[0]

        workSpaceLocation[0:2]=camNpLocation[0:2]+np.array([xPx,yPx])

        return workSpaceLocation

if False:
    camSensor=CamSensor(toolCamera)
    filePath="/media/bcastets/data/racine/Loisir/wordPress/articles/cobot/illustration/blender/render/gameImage.png"
