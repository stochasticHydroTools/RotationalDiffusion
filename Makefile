# location of the Python header files
 
PYTHON_VERSION = 2.7
PYTHON_INCLUDE = /usr/include/python$(PYTHON_VERSION)
 
# location of the Boost Python include files and library
 
#BOOST_INC = /usr/include  #original version
BOOST_INC = /opt/local/include  #Mac version
# BOOST_LIB = /usr/lib  #original version
BOOST_LIB = /opt/local/lib  #Mac version
 
# compile mesh classes
TARGET = constrained_diff_ext
 
#-Wl,--export-dynamic
$(TARGET).so: $(TARGET).o
	g++ -shared  $(TARGET).o -L$(BOOST_LIB)  -lboost_python-mt -L/usr/lib/python$(PYTHON_VERSION)/config -lpython$(PYTHON_VERSION) -o $(TARGET).so

 
$(TARGET).o: $(TARGET).cc
	g++ -I$(PYTHON_INCLUDE) -I$(BOOST_INC) -fPIC -c $(TARGET).cc

clean: 
	rm -f $(TARGET).o $(TARGET).so

