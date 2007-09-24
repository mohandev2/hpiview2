#!/usr/bin/env python


import wx
import sys, os
from openhpi import *
import ResourcePref
import SensorPref
import ControlPref
import InventoryPref
import WatchdogPref

class Hpiview_Callbacks:

    frame = None
    sid = None
    dinfo = None
    Status = None	    	
    res = None
    rdr = None		
    rdrlist = None
    item_clicked = None	
    menu_titles = {}
    ResourceTitles = ["EventLog","Event Log Timestamp", "Event Log Clear", "-", "Parameter Control", "Power", "reset", "-", "Preferences"] 	
    SensorTitles = ["Read Sensor", "-", "Preferences"]
    ControlTitles = ["Preferences"]
    WatchdogTitles = ["Reset Watchdog", "-", "Preferences"]
    InventoryTitles = ["Preferences"]
    menu_type = ""	
	
    menu_title_by_id = {}
		
    def __init__(self, fr):
	global frame
	global rdrlist
	frame = fr
	frame.Bind(wx.EVT_MENU, self.Menu_Session_Quit_Handler)
	frame.Bind(wx.EVT_TOOL, self.CLose_Button_Handler)   
	frame.Bind(wx.EVT_BUTTON, self.New_Session_Handler, frame.bitmap_button_2)
	frame.Bind(wx.EVT_BUTTON, self.Hide_Domain_Handler, frame.bitmap_button_1)	
	frame.Bind(wx.EVT_LISTBOX_DCLICK, self.Set_TreeOnNewSession, frame.list_box_1)
	frame.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.sys_activated, frame.tree_ctrl_1)	
	frame.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.sys_collapsed, frame.tree_ctrl_1)
	frame.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.sys_expanded, frame.tree_ctrl_1)
	frame.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.RightClickCb ,frame.tree_ctrl_1)
	rdrlist=[["x",0,0,0]]

    def openHpiSession(self):
	global sid
	error, sid = saHpiSessionOpen(SAHPI_UNSPECIFIED_DOMAIN_ID, None)
	print "Session opened"
	return 
		
    def discover(self):
	global dinfo
	error = saHpiDiscover(sid)
	dinfo = SaHpiDomainInfoT()
	error = saHpiDomainInfoGet(sid, dinfo)
	return

    def SubscribeEvents(self):
	global sid
	error = saHpiSubscribe(sid)
	return	

    def unSubscribeEvents(self):
	global sid
	error = saHpiUnsubscribe(sid)
	return	

    def polpulateResAndRdrTypeData(self):
	global frame,sid , res , rdr ,rdrlist
	first = True
	firstroot = True
	addChildsToRoot = False
	tbuff = None
	textbuffer = oh_big_textbuffer()
    	res = SaHpiRptEntryT()
    	rdr = SaHpiRdrT()
	eid = SAHPI_FIRST_ENTRY
	error = SA_OK
	error1 = SA_OK
	while error == SA_OK and eid != SAHPI_LAST_ENTRY:

		erid = SAHPI_FIRST_ENTRY

		error, nexteid = saHpiRptEntryGet(sid, eid, res)

		if error == SA_OK:
			rid = res.ResourceId


			if res.ResourceCapabilities & SAHPI_CAPABILITY_RDR:
			
				while error1 == SA_OK and  erid != SAHPI_LAST_ENTRY:

					error1 , nextrdrid = saHpiRdrGet(sid , rid , erid , rdr)

					if(firstroot):
						tbuff = oh_big_textbuffer()
						oh_init_bigtext(tbuff)
						oh_decode_entitypath(rdr.Entity, tbuff)
						frame.tree_ctrl_1.AddRoot(tbuff.Data,-1,-1,None)
						rdrlist.append([tbuff.Data,res.ResourceId,res.ResourceEntity,res.ResourceCapabilities,res.HotSwapCapabilities,res.ResourceTag.Data,res.ResourceSeverity])
						firstroot=False
						tbuff = None

					if(addChildsToRoot):				
						tbuff = oh_big_textbuffer()
						oh_init_bigtext(tbuff)
						oh_decode_entitypath(rdr.Entity, tbuff)
						frame.tree_ctrl_1.AppendItem(frame.tree_ctrl_1.GetRootItem(),tbuff.Data,-1,-1,None)
						rdrlist.append([tbuff.Data,res.ResourceId,res.ResourceEntity,res.ResourceCapabilities,res.HotSwapCapabilities,res.ResourceTag.Data,res.ResourceSeverity])
						addChildsToRoot=False
						tbuff = None

					if(first):
						if(rdr.RdrType == SAHPI_SENSOR_RDR):
							frame.tree_ctrl_1.AppendItem(frame.tree_ctrl_1.GetRootItem(),str(oh_lookup_sensortype(rdr.RdrTypeUnion.SensorRec.Type)) + " Sensor",-1,-1,None)			
							rdrlist.append([str(oh_lookup_sensortype(rdr.RdrTypeUnion.SensorRec.Type)) + " Sensor",rdr.RdrTypeUnion.SensorRec.Num,rid,rdr.RdrType,rdr.RdrTypeUnion.SensorRec.DataFormat,rdr.RdrTypeUnion.SensorRec.DataFormat.BaseUnits,rdr.RdrTypeUnion.SensorRec.Type,rdr.RdrTypeUnion.SensorRec.EnableCtrl,rdr.RdrTypeUnion.SensorRec.EventCtrl,rdr.RdrTypeUnion.SensorRec.DataFormat.Range.Min.Value.SensorFloat64,rdr.RdrTypeUnion.SensorRec.DataFormat.Range.Max.Value.SensorFloat64,rdr.RdrTypeUnion.SensorRec.DataFormat.Range.Nominal.Value.SensorFloat64,rdr.RdrTypeUnion.SensorRec.DataFormat.Range.NormalMin.Value.SensorFloat64,rdr.RdrTypeUnion.SensorRec.DataFormat.Range.NormalMax.Value.SensorFloat64,rdr.IsFru])
						if(rdr.RdrType == SAHPI_CTRL_RDR):
							frame.tree_ctrl_1.AppendItem(frame.tree_ctrl_1.GetRootItem(),str(oh_lookup_ctrltype(rdr.RdrTypeUnion.CtrlRec.Type)) + " Control",-1,-1,None)			
							rdrlist.append([str(oh_lookup_ctrltype(rdr.RdrTypeUnion.CtrlRec.Type))+ " Control",rdr.RdrTypeUnion.CtrlRec.Num,rid,rdr.RdrType,rdr.RdrTypeUnion.CtrlRec.Type,rdr.RdrTypeUnion.CtrlRec.OutputType,rdr.IsFru])
						if(rdr.RdrType == SAHPI_WATCHDOG_RDR):
							frame.tree_ctrl_1.AppendItem(frame.tree_ctrl_1.GetRootItem(),"WatchDog  "+ str(rdr.RdrTypeUnion.WatchdogRec.WatchdogNum),-1,-1,None)			
							rdrlist.append(["WatchDog  "+str(rdr.RdrTypeUnion.WatchdogRec.WatchdogNum),rdr.RdrTypeUnion.WatchdogRec.WatchdogNum,rid,rdr.RdrType,rdr.IsFru])
						if(rdr.RdrType == SAHPI_INVENTORY_RDR):
							frame.tree_ctrl_1.AppendItem(frame.tree_ctrl_1.GetRootItem(),"Simulator Inv "+str(rdr.RdrType),-1,-1,None)			
							rdrlist.append(["Simulator Inv "+str(rdr.RdrType),rdr.RdrType,rid,rdr.RdrType,rdr.IsFru,rdr.RdrTypeUnion.InventoryRec.Persistent])
						if(rdr.RdrType == SAHPI_ANNUNCIATOR_RDR):
							frame.tree_ctrl_1.AppendItem(frame.tree_ctrl_1.GetRootItem(),"Annunciator "+ str(rdr.RdrTypeUnion.AnnunciatorRec.AnnunciatorNum),-1,-1,None)			
							rdrlist.append(["Annunciator "+ str(rdr.RdrTypeUnion.AnnunciatorRec.AnnunciatorNum),rdr.RdrTypeUnion.AnnunciatorRec.AnnunciatorNum,rid,rdr.RdrType,rdr.RdrTypeUnion.AnnunciatorRec.AnnunciatorType,rdr.IsFru])

					if(first == False):
						if(rdr.RdrType == SAHPI_SENSOR_RDR):
							frame.tree_ctrl_1.AppendItem(frame.tree_ctrl_1.GetLastChild(frame.tree_ctrl_1.GetRootItem()),str(oh_lookup_sensortype(rdr.RdrTypeUnion.SensorRec.Type)) + " Sensor",-1,-1,None)			
							rdrlist.append([str(oh_lookup_sensortype(rdr.RdrTypeUnion.SensorRec.Type))+" Sensor",rdr.RdrTypeUnion.SensorRec.Num,rid,rdr.RdrType,rdr.RdrTypeUnion.SensorRec.DataFormat,rdr.RdrTypeUnion.SensorRec.DataFormat.BaseUnits,rdr.RdrTypeUnion.SensorRec.Type,rdr.RdrTypeUnion.SensorRec.EnableCtrl,rdr.RdrTypeUnion.SensorRec.EventCtrl,rdr.RdrTypeUnion.SensorRec.DataFormat.Range.Min.Value.SensorFloat64,rdr.RdrTypeUnion.SensorRec.DataFormat.Range.Max.Value.SensorFloat64,rdr.RdrTypeUnion.SensorRec.DataFormat.Range.Nominal.Value.SensorFloat64,rdr.RdrTypeUnion.SensorRec.DataFormat.Range.NormalMin.Value.SensorFloat64,rdr.RdrTypeUnion.SensorRec.DataFormat.Range.NormalMax.Value.SensorFloat64,rdr.IsFru])
						if(rdr.RdrType == SAHPI_CTRL_RDR):						
							frame.tree_ctrl_1.AppendItem(frame.tree_ctrl_1.GetLastChild(frame.tree_ctrl_1.GetRootItem()),str(oh_lookup_ctrltype(rdr.RdrTypeUnion.CtrlRec.Type)) + " Control",-1,-1,None)			
							rdrlist.append([str(oh_lookup_ctrltype(rdr.RdrTypeUnion.CtrlRec.Type))+" Control",rdr.RdrTypeUnion.CtrlRec.Num,rid,rdr.RdrType,rdr.RdrTypeUnion.CtrlRec.Type,rdr.RdrTypeUnion.CtrlRec.OutputType,rdr.IsFru])
						if(rdr.RdrType == SAHPI_WATCHDOG_RDR):
							frame.tree_ctrl_1.AppendItem(frame.tree_ctrl_1.GetLastChild(frame.tree_ctrl_1.GetRootItem()),"WatchDog  "+ str(rdr.RdrTypeUnion.WatchdogRec.WatchdogNum),-1,-1,None)			
							rdrlist.append(["WatchDog  "+str(rdr.RdrTypeUnion.WatchdogRec.WatchdogNum),rdr.RdrTypeUnion.WatchdogRec.WatchdogNum,rid,rdr.RdrType,rdr.IsFru])
						if(rdr.RdrType == SAHPI_INVENTORY_RDR):
							frame.tree_ctrl_1.AppendItem(frame.tree_ctrl_1.GetLastChild(frame.tree_ctrl_1.GetRootItem()),"Simulator Inv "+str(rdr.RdrType),-1,-1,None)			
							rdrlist.append(["Simulator Inv "+str(rdr.RdrType),rdr.RdrType,rid,rdr.RdrType,rdr.IsFru,rdr.RdrTypeUnion.InventoryRec.Persistent])
						if(rdr.RdrType == SAHPI_ANNUNCIATOR_RDR):
							frame.tree_ctrl_1.AppendItem(frame.tree_ctrl_1.GetLastChild(frame.tree_ctrl_1.GetRootItem()),"Annunciator "+ str(rdr.RdrTypeUnion.AnnunciatorRec.AnnunciatorNum),-1,-1,None)			
							rdrlist.append(["Annunciator "+ str(rdr.RdrTypeUnion.AnnunciatorRec.AnnunciatorNum),rdr.RdrTypeUnion.AnnunciatorRec.AnnunciatorNum,rid,rdr.RdrType,rdr.RdrTypeUnion.AnnunciatorRec.AnnunciatorType,rdr.IsFru])

					erid = nextrdrid
		

			else:
				dbg('Resource doesn\'t have RDR')

		first = False
		eid = nexteid
		if(eid > 1):
			addChildsToRoot=True
	
		print 'rptentry[%u] tag: %s' % (res.ResourceId, res.ResourceTag.Data)

	return	

    def popualateRDRData(self):	
	return

    def dbg(format, vals=()):
	"""Prints message only if verbose is turned on"""
	if options.verbose:
		print format % vals

    def errorout(format, error):
	"""Prints HPI error and exits"""
	if error != SA_OK:
		print format % oh_lookup_error(error)
		sys.exit(-1)

    def sys_activated(self, event): # wxGlade: MyFrame.<event_handler>
	global frame
	global rdrlist
	global sid
	reading = None
	evtState = None
	textbuffer = oh_big_textbuffer()
	error = SA_OK
	frame.text_ctrl_1.SetValue(frame.tree_ctrl_1.GetItemText(frame.tree_ctrl_1.GetSelection()))
	for ind in range(0,len(rdrlist)):
		if(rdrlist[ind][0] == frame.text_ctrl_1.GetValue()):
			if(rdrlist[ind][3]==SAHPI_SENSOR_RDR):
				oh_init_bigtext(textbuffer)
				reading = SaHpiSensorReadingT()
				textbuffer = SaHpiTextBufferT()
				error ,evtState = saHpiSensorReadingGet(sid,rdrlist[ind][2],rdrlist[ind][1],reading)
				#oh_decode_sensorreading(reading,rdrlist[ind][4],textbuffer)
				oh_append_textbuffer(textbuffer,"\n"+" Type 			\t"+"Sensor \n")
				#stype = SaHpiSensorTypeT()
				#stype ,evtState = saHpiSensorTypeGet(sid,rdrlist[ind][2],rdrlist[ind][1])
				#oh_append_textbuffer(textbuffer,"\n"+" FRU Entity 		\t"+str(rdrlist[ind][14])+"\n")
				if(rdrlist[ind][14]==0):
					oh_append_textbuffer(textbuffer,"\n"+" FRU Entity 		\t"+ "False" +"\n")
				else:
					oh_append_textbuffer(textbuffer,"\n"+" FRU Entity 		\t"+ "True" +"\n")
				oh_append_textbuffer(textbuffer,"\n"+" Sensor Type 		\t"+str(oh_lookup_sensortype(rdrlist[ind][6]))+"\n")
				oh_append_textbuffer(textbuffer,"\n"+" Sensor Base Unit 	\t"+str(oh_lookup_sensorunits(rdrlist[ind][5]))+"\n")
				#oh_append_textbuffer(textbuffer,"\n"+" Sensor Control 	\t"+str(rdrlist[ind][7])+"\n")
				if(rdrlist[ind][7]==0):
					oh_append_textbuffer(textbuffer,"\n"+" Sensor Control 	\t"+ "False" +"\n")
				else:
					oh_append_textbuffer(textbuffer,"\n"+" Sensor Control 	\t"+ "True" +"\n")
				oh_append_textbuffer(textbuffer,"\n"+" Event Control 	\t"+str(oh_lookup_sensoreventctrl(rdrlist[ind][8]))+"\n")
				oh_append_textbuffer(textbuffer,"\n"+" Min Value 		\t"+str(rdrlist[ind][9])+"\n")
				oh_append_textbuffer(textbuffer,"\n"+" Max Value 		\t"+str(rdrlist[ind][10])+"\n")
				oh_append_textbuffer(textbuffer,"\n"+" Nominal Value 	\t"+str(rdrlist[ind][11])+"\n")
				oh_append_textbuffer(textbuffer,"\n"+" Normal MinValue 	\t"+str(rdrlist[ind][12])+"\n")
				oh_append_textbuffer(textbuffer,"\n"+" Normal MaxValue 	\t"+str(rdrlist[ind][13])+"\n")
				frame.text_ctrl_1.SetValue(textbuffer.Data)
				continue
			if(rdrlist[ind][3]==SAHPI_CTRL_RDR):
				#textbuffer = oh_init_bigtext(textbuffer)
				ctrlState = SaHpiCtrlStateT()
				textbuffer = SaHpiTextBufferT()
				error ,Mode = saHpiControlGet(sid,rdrlist[ind][2],rdrlist[ind][1],ctrlState)
				#oh_decode_sensorreading(reading,rdr.RdrTypeUnion.SensorRec.DataFormat,textbuffer)
				oh_append_textbuffer(textbuffer,"\n"+" Type 			\t"+"Control"+"\n")
				#oh_append_textbuffer(textbuffer,"\n"+" FRU Entity 		\t"+str(rdrlist[ind][6])+"\n")
				if(rdrlist[ind][6]==0):
					oh_append_textbuffer(textbuffer,"\n"+" FRU Entity 		\t"+ "False" +"\n")
				else:
					oh_append_textbuffer(textbuffer,"\n"+" FRU Entity 		\t"+ "True" +"\n")
				oh_append_textbuffer(textbuffer,"\n" +" Control Type 		\t"+str(oh_lookup_ctrltype(rdrlist[ind][4]))+"\n")
				oh_append_textbuffer(textbuffer,"\n" +" Control Output Type \t" + str(oh_lookup_ctrloutputtype(rdrlist[ind][5]))+"\n")
				oh_append_textbuffer(textbuffer,"\n" +" Control State Digital\t"+str(oh_lookup_ctrlstatedigital(ctrlState.StateUnion.Digital))+"\n")
				oh_append_textbuffer(textbuffer,"\n" +" Mode 			\t"+str(oh_lookup_ctrlmode(Mode))+"\n")
				#oh_append_textbuffer(textbuffer,"Max Value \t"+str(rdr.RdrTypeUnion.SensorRec.DataFormat.Range.Max.Value.SensorFloat64)+"\n")
				#oh_append_textbuffer(textbuffer,"Nominal Value \t"+str(rdr.RdrTypeUnion.SensorRec.DataFormat.Range.Nominal.Value.SensorFloat64)+"\n")
				#oh_append_textbuffer(textbuffer,"Normal MinValue \t"+str(rdr.RdrTypeUnion.SensorRec.DataFormat.Range.NormalMin.Value.SensorFloat64)+"\n")
				#oh_append_textbuffer(textbuffer,"Normal MaxValue \t"+str(rdr.RdrTypeUnion.SensorRec.DataFormat.Range.NormalMax.Value.SensorFloat64)+"\n")
				frame.text_ctrl_1.SetValue(textbuffer.Data)
				continue
			if(rdrlist[ind][3]==SAHPI_WATCHDOG_RDR):
				textbuffer = SaHpiTextBufferT()
				watchdogt = SaHpiWatchdogT()
				error = saHpiWatchdogTimerGet(sid,rdrlist[ind][2],rdrlist[ind][1],watchdogt)
				#oh_decode_sensorreading(reading,rdr.RdrTypeUnion.SensorRec.DataFormat,textbuffer)
				oh_append_textbuffer(textbuffer,"\n"+ " Type 			\t"+"WatchDog"+"\n")
				#oh_append_textbuffer(textbuffer,"\n"+" FRU Entity 		\t"+str(rdrlist[ind][4])+"\n")
				if(rdrlist[ind][4]==0):
					oh_append_textbuffer(textbuffer,"\n"+" FRU Entity 		\t"+ "False" +"\n")
				else:
					oh_append_textbuffer(textbuffer,"\n"+" FRU Entity 		\t"+ "True" +"\n")
				oh_append_textbuffer(textbuffer,"\n"+ " Watch Dog Action 	\t"+str(oh_lookup_watchdogaction(watchdogt.TimerAction))+"\n")
				#oh_append_textbuffer(textbuffer,"Watch Dog Action Event \t" + str(oh_lookup_watchdogactionevent())+"\n")
				oh_append_textbuffer(textbuffer,"\n"+ " Pre timer interrupt \t"+str(oh_lookup_watchdogpretimerinterrupt(watchdogt.PretimerInterrupt))+"\n")
				oh_append_textbuffer(textbuffer,"\n"+ " Timer use 		\t"+str(oh_lookup_watchdogtimeruse(watchdogt.TimerUse))+"\n")
				#oh_append_textbuffer(textbuffer,"Max Value \t"+str(rdr.RdrTypeUnion.SensorRec.DataFormat.Range.Max.Value.SensorFloat64)+"\n")
				#oh_append_textbuffer(textbuffer,"Nominal Value \t"+str(rdr.RdrTypeUnion.SensorRec.DataFormat.Range.Nominal.Value.SensorFloat64)+"\n")
				#oh_append_textbuffer(textbuffer,"Normal MinValue \t"+str(rdr.RdrTypeUnion.SensorRec.DataFormat.Range.NormalMin.Value.SensorFloat64)+"\n")
				#oh_append_textbuffer(textbuffer,"Normal MaxValue \t"+str(rdr.RdrTypeUnion.SensorRec.DataFormat.Range.NormalMax.Value.SensorFloat64)+"\n")
				frame.text_ctrl_1.SetValue(textbuffer.Data)
				continue
			if(rdrlist[ind][3]==SAHPI_ANNUNCIATOR_RDR):
				textbuffer = SaHpiTextBufferT()
				annunt = SaHpiAnnouncementT()
				error = saHpiAnnunciatorGet(sid,rdrlist[ind][2],rdrlist[ind][1],SAHPI_FIRST_ENTRY,annunt)
				#oh_decode_sensorreading(reading,rdr.RdrTypeUnion.SensorRec.DataFormat,textbuffer)
				oh_append_textbuffer(textbuffer,"\n"+" Type 			\t"+"Annunciator"+"\n")
				#oh_append_textbuffer(textbuffer,"\n"+" FRU Entity 		\t"+str(rdrlist[ind][5])+"\n")
				if(rdrlist[ind][5]==0):
					oh_append_textbuffer(textbuffer,"\n"+" FRU Entity 		\t"+ "False" +"\n")
				else:
					oh_append_textbuffer(textbuffer,"\n"+" FRU Entity 		\t"+ "True" +"\n")
				#oh_append_textbuffer(textbuffer,"Annunciator Mode \t"+str(oh_lookup_annunciatormode(watchdogt.TimerAction))+"\n")
				oh_append_textbuffer(textbuffer,"\n"+" Annunciator Type 	\t" + str(oh_lookup_annunciatortype(rdrlist[ind][4]))+"\n")
				frame.text_ctrl_1.SetValue(textbuffer.Data)
				continue
			if(rdrlist[ind][3]==SAHPI_INVENTORY_RDR):
				textbuffer = SaHpiTextBufferT()
				idrinfo = SaHpiIdrInfoT()
				error = saHpiIdrInfoGet(sid,rdrlist[ind][2],rdrlist[ind][1],idrinfo)
				oh_append_textbuffer(textbuffer,"\n"+" Type 			\t"+"Inventory"+"\n")
				#oh_append_textbuffer(textbuffer,"\n"+" FRU Entity 		\t"+str(rdrlist[ind][4])+"\n")
				if(rdrlist[ind][4]==0):
					oh_append_textbuffer(textbuffer,"\n"+" FRU Entity 		\t"+ "False" +"\n")
				else:
					oh_append_textbuffer(textbuffer,"\n"+" FRU Entity 		\t"+ "True" +"\n")
				#oh_append_textbuffer(textbuffer,"\n"+" Inventory's Persistent \t"+str(rdrlist[ind][5])+"\n")
				if(rdrlist[ind][5]==0):
					oh_append_textbuffer(textbuffer,"\n"+" Inventory's Persistent \t"+ "False" +"\n")
				else:
					oh_append_textbuffer(textbuffer,"\n"+" Inventory's Persistent \t"+ "True" +"\n")
				frame.text_ctrl_1.SetValue(textbuffer.Data)
				continue

  			textbuffer = SaHpiTextBufferT()
  			t1 = SaHpiTextBufferT()
			#entryid = SaHpiEntryIdT()
			#error = saHpiRptEntryGet(
			oh_append_textbuffer(textbuffer,"\n"+" ResourceID	\t" + str(rdrlist[ind][1])+"\n")
			oh_append_textbuffer(textbuffer,"\n"+" Entity Path 	\t" + rdrlist[ind][0]+"\n")
			oh_decode_capabilities(rdrlist[ind][3],t1)
			oh_append_textbuffer(textbuffer,"\n"+" Capabilities	\t" + t1.Data+"\n")
			oh_append_textbuffer(textbuffer,"\n"+" HotSwap Capabilities \t" + str(rdrlist[ind][4])+"\n")
			oh_append_textbuffer(textbuffer,"\n"+" Resource Tag	\t" + rdrlist[ind][5]+"\n")
			oh_append_textbuffer(textbuffer,"\n"+" Severity		\t" + str(rdrlist[ind][6])+"\n")
			frame.text_ctrl_1.SetValue(textbuffer.Data)
				
    def sys_collapsed(self, event): # wxGlade: MyFrame.<event_handler>
        print "Event handler `sys_collapsed' not implemented!"
        event.Skip()

    def sys_expanded(self, event): # wxGlade: MyFrame.<event_handler>
        print "Event handler `sys_expanded' not implemented!"
        event.Skip()

    def Menu_Session_Quit_Handler(self, event): # wxGlade: MyFrame.<event_handler>
	global frame
	global sid
        print "Event handler `Menu_Session_Quit_Handler' not implemented"
	saHpiSessionClose(sid)
        frame.DestroyChildren()
	frame.Destroy()
	#event.Skip(True)
    
    def Set_TreeOnNewSession(self, event): # wxGlade: MyFrame.<event_handler>
	global frame
	self.polpulateResAndRdrTypeData()

    
    def CLose_Button_Handler(self, event): # wxGlade: MyFrame.<event_handler>
	global frame
	global sid
	#error = saHpiSessionClose(sid)
	frame.list_box_1.Delete(frame.list_box_1.GetSelection())
        frame.tree_ctrl_1.DeleteAllItems()
        frame.text_ctrl_1.Clear()
        frame.notebook_1.Show(False)
	#event.Skip(True)
    
    def Hide_Domain_Handler(self, event): # wxGlade: MyFrame.<event_handler>
	global frame
        if(frame.list_box_1.IsShown() == False):
            frame.list_box_1.Show(show=True)
        else:
	    if(frame.list_box_1.IsShown() == True):
	    	frame.list_box_1.Show(show=False)

    def New_Session_Handler(self, event): # wxGlade: MyFrame.<event_handler>
	global frame
        frame.tree_ctrl_1.DeleteAllItems()
	if(frame.list_box_1.GetCount() < 1):
	        frame.list_box_1.Insert("DEFAULT",frame.list_box_1.GetCount(),None)
        frame.notebook_1.Show(True)
	self.openHpiSession()
	self.polpulateResAndRdrTypeData()

    def RightClickCb( self, event ):

	global frame,item_clicked

        # record what was clicked
        item_clicked = frame.tree_ctrl_1.GetItemText(event.GetItem())

	self.menu_titles={}
	self.menu_title_by_id={}

	if(item_clicked.find(",") > 0 ):
	   self.menu_titles = self.ResourceTitles
	   self.menu_type="Resource"	
	if(item_clicked.find("Sensor") > 0):
	   self.menu_titles = self.SensorTitles	
	   self.menu_type="Sensor"	
	if(item_clicked.find("Control") > 0):
	   self.menu_titles = self.ControlTitles	
	   self.menu_type="Control"	
	if(item_clicked.find("Dog") > 0):
	   self.menu_titles = self.WatchdogTitles	
	   self.menu_type="WatchDog"	
	if(item_clicked.find("Inv") > 0):
	   self.menu_titles = self.InventoryTitles	
	   self.menu_type="Inventory"	

	for title in self.menu_titles:
	  self.menu_title_by_id[ wx.NewId() ] = title

	print item_clicked
 
        ### 2. Launcher creates wxMenu. ###
        menu = wx.Menu()
        for (id,title) in self.menu_title_by_id.items():
            ### 3. Launcher packs menu with Append. ###
            menu.Append( id, title )
            ### 4. Launcher registers menu handlers with EVT_MENU, on the menu. ###
            wx.EVT_MENU( menu, id, self.MenuSelectionCb )
 
        ### 5. Launcher displays menu with call to PopupMenu, invoked on the source component, passing event's GetPoint. ###
        frame.tree_ctrl_1.PopupMenu( menu, event.GetPoint() )

    def MenuSelectionCb( self, event ):

        # do something
        operation = self.menu_title_by_id[ event.GetId() ]
        target    = self.item_clicked
        print 'Perform "%(operation)s" on "%(target)s."' % vars()

	if(self.menu_type == "Resource" and operation == self.ResourceTitles[len(self.ResourceTitles)-1]):
		frm = ResourcePref.frmResPref(frame,-1,"")
		frm.Show()
	if(self.menu_type == "Sensor" and operation == self.SensorTitles[len(self.SensorTitles)-1]):
		frm = SensorPref.frmSenPref(frame,-1,"")
		frm.Show()
	if(self.menu_type == "Control" and operation == self.ControlTitles[len(self.ControlTitles)-1]):
		frm = ControlPref.frmCtrlPref(frame,-1,"")
		frm.Show()
	if(self.menu_type == "Inventory" and operation == self.InventoryTitles[len(self.InventoryTitles)-1]):
		frm = InventoryPref.frmInvPref(frame,-1,"")
		frm.Show()
	if(self.menu_type == "WatchDog" and operation == self.WatchdogTitles[len(self.WatchdogTitles)-1]):
		frm = WatchdogPref.frmWatchdogPref(frame,-1,"")
		frm.Show()
