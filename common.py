import sys, math, Image, os
import logging, numpy as np
import cv2


def configureLogging(loglevel):
  numeric_level = getattr(logging, loglevel.upper(), None)
  if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % loglevel)
  logging.basicConfig(level=numeric_level, format='%(levelname)s:%(funcName)s:%(message)s')


def loadCascadeClassifier(filename):
  cascade = cv2.CascadeClassifier(filename)
  if cascade.empty():
    raise ValueError('Cascade classifier is empty!')

  return cascade


def drawLabel(text, image, position):
  fontFace = cv2.FONT_HERSHEY_SIMPLEX
  scale = 0.6;
  thickness = 1;
  filledThickness = -1

  (x,y) = position
  ((textSizeX, textSizeY), _) = cv2.getTextSize(text, fontFace, scale, thickness)
  rectA = (x-5,y+5)
  rectB = (x+textSizeX+5, y-5-textSizeY)

  overlay = image.copy()
  cv2.rectangle(overlay, rectA, rectB, (0,0,0), filledThickness);
  cv2.putText(overlay, text, position, fontFace, scale, (255,255,255), thickness);

  opacity = 0.4
  cv2.addWeighted(overlay, opacity, image, 1 - opacity, 0, image)


def calculateScaledSize(image, outputWidth):
  height, width = image.shape[:2]
  proportionalHeight = int(outputWidth * height / width)
  return (outputWidth, proportionalHeight)

def resizeImage(image, size):
  # resize to given size (if given)
  if (size is None):
    return image
  else:
    return image.resize(size, Image.ANTIALIAS)


def readImages(paths, sz=None):
  """Reads the images in a given folder, resizes images on the fly if size is given.

  Args:
      path: Path to a folder with subfolders representing the subjects (persons).
      sz: A tuple with the size Resizes 

  Returns:
      A list [images,y]

          images: The images, which is a Python list of numpy arrays.
          labels: The corresponding labels (the unique number of the subject, person) in a Python list.
  """
  subjectId = 0
  images,labels, subjects = [], [], []
  for path in paths:
    logging.debug('Reading files from {0}'.format(path))
    fileCount = 0
    totalFilesCount = sum([len(files) for r, d, files in os.walk(path)])
    print 'Reading directory {0}... '.format(path)
    for dirname, dirnames, filenames in os.walk(path):
      for subdirname in dirnames:
        subject_path = os.path.join(dirname, subdirname)
        for filename in os.listdir(subject_path):
          try:
            im = Image.open(os.path.join(subject_path, filename))
            im = resizeImage(im.convert("L"), sz)
            images.append(np.asarray(im, dtype=np.uint8))
            labels.append(subjectId)
            fileCount += 1
            sys.stdout.write("Loaded file {0} of {1}      \r".format(fileCount, totalFilesCount))
            sys.stdout.flush()
          except IOError, (errno, strerror):
            print "I/O error({0}): {1}".format(errno, strerror)
          except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        subjects.append(subdirname)
        subjectId += 1
    print('')

  return [images, np.asarray(labels, dtype=np.int32), subjects]


def detectFaces(image, faceCascade, leftEyeCascade, rightEyeCascade, 
  minFaceSize = (100, 100), minEyeSize = (12, 18), mouthCascade = None):
  logging.debug("Detecting faces...")
  faceCandidates = detectElements(image, faceCascade, minFaceSize, 0)
  faces = []

  for (x, y, w, h) in faceCandidates:
    logging.debug("Detected possible face: ({0},{1},{2},{3})".format(x,y,w,h))
    tempFace = image[y:y+h, x:x+w]
    faceUpper = tempFace[0:int(6*h/10), 0:w]

    leftEyes = detectElements(faceUpper, leftEyeCascade, minEyeSize, 0)
    rightEyes = detectElements(faceUpper, rightEyeCascade, minEyeSize, 0)

    if len(leftEyes) > 0 and len(rightEyes) > 0:
      logging.info("Detected possible face with {0} right eyes and {1} left eyes.".format(len(rightEyes), len(rightEyes)))

      if not mouthCascade is None:
        faceLower = tempFace[int(6.5*h/10):h, 0:w]
        mouths = detectElements(faceLower, mouthCascade, minFaceSize, 0)

        if len(mouths) > 1:
          logging.info("Detected face with {0} mouths.".format(len(mouths)))
          faces.append((x, y, w, h, leftEyes[0], rightEyes[0], mouths))
      else:
        faces.append((x, y, w, h, leftEyes[0], rightEyes[0], None))

  return faces


def detectElements(image, elementCascade, minSizeElem, recursiveSizeStep=0):
  haar_scale = 1.1
  min_neighbors = 3

  # Convert color input image to grayscale
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  # Equalize the histogram
  gray = cv2.equalizeHist(gray)

  elements = elementCascade.detectMultiScale(gray, scaleFactor=haar_scale, minNeighbors=min_neighbors, minSize=minSizeElem)

  if (elements == () or len(elements) == 0):
    if recursiveSizeStep == 0:
      logging.debug("No elements found!")
      return []
    else:
      s1, s2 = minSizeElem
      logging.debug("No elements yet! Recursive call...")
      return DetectElements(image, elementCascade, (s1 - recursiveSizeStep, s2 - recursiveSizeStep))
  else:
    logging.debug("Elements found:")
    logging.debug(elements)       

    return elements


def calculateCenter(square):
  (a, b, w, h) = square
  wOffset = int(w/2)
  hOffset = int(h/2)
  return (a + wOffset, b + hOffset)


def Distance(p1,p2):
  dx = p2[0] - p1[0]
  dy = p2[1] - p1[1]
  return math.sqrt(dx*dx+dy*dy)


def ScaleRotateTranslate(image, angle, center = None, new_center = None, scale = None, resample=Image.BICUBIC):
  if (scale is None) and (center is None):
    return image.rotate(angle=angle, resample=resample)
  nx,ny = x,y = center
  sx=sy=1.0
  if new_center:
    (nx,ny) = new_center
  if scale:
    (sx,sy) = (scale, scale)
  cosine = math.cos(angle)
  sine = math.sin(angle)
  a = cosine/sx
  b = sine/sx
  c = x-nx*a-ny*b
  d = -sine/sy
  e = cosine/sy
  f = y-nx*d-ny*e
  return image.transform(image.size, Image.AFFINE, (a,b,c,d,e,f), resample=resample)


def cropFace(image, eye_left, eye_right, offset_pct=(0.3,0.3), dest_sz = (92,112)):
  image = Image.fromarray(np.uint8(image))
  # calculate offsets in original image
  offset_h = math.floor(float(offset_pct[0])*dest_sz[0])
  offset_v = math.floor(float(offset_pct[1])*dest_sz[1])
  # get the direction
  eye_direction = (eye_right[0] - eye_left[0], eye_right[1] - eye_left[1])
  # calc rotation angle in radians
  rotation = -math.atan2(float(eye_direction[1]),float(eye_direction[0]))
  # distance between them
  dist = Distance(eye_left, eye_right)
  # calculate the reference eye-width
  reference = dest_sz[0] - 2.0*offset_h
  # scale factor
  scale = float(dist)/float(reference)
  logging.debug("Scale and rotating to center: {0} and angle: {1}".format(eye_left, rotation))
  # rotate original around the left eye
  image = ScaleRotateTranslate(image, center=eye_left, angle=rotation)
  # crop the rotated image
  crop_xy = (eye_left[0] - scale*offset_h, eye_left[1] - scale*offset_v)
  crop_size = (dest_sz[0]*scale, dest_sz[1]*scale)
  image = image.crop((int(crop_xy[0]), int(crop_xy[1]), int(crop_xy[0]+crop_size[0]), int(crop_xy[1]+crop_size[1])))
  # resize it
  image = image.resize(dest_sz, Image.ANTIALIAS)
  return np.array(image)
