cmake_minimum_required(VERSION 2.8.9)

project(Slicer-CameraDriver)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/lchauvin/Slicer-CameraDriver")
set(EXTENSION_CATEGORY "Examples")
set(EXTENSION_CONTRIBUTORS "John Doe (AnyWare Corp.)")
set(EXTENSION_DESCRIPTION "This is an example of a simple extension")
set(EXTENSION_ICONURL "https://raw.github.com/lchauvin/Slicer-CameraDriver/master/Slicer-CameraDriver.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/Slicer-CameraDriver/Screenshots/1.png")

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(CameraDriver)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
