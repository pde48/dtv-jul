# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
import codecs
import base64
from datetime import datetime,timedelta
import json
import time
import csv

class modulo_data(models.Model):
	_name = 'modulo.data'

	file = fields.Binary('Archivo CSV' )
	#ubicacion = fields.Many2one('stock.location',string='Ubicación')
	id_mensajes_crm=fields.Char('')
	id_mensajes_helpdesk=fields.Char('')
	bandera = fields.Boolean(string='activador',default=True)
	tablas=fields.Selection([('res_users','res.users'),('res_partner','res.partner'),
								('crm_team','crm.team'),('crm_stage','crm.stage'),('crm_lead','crm.lead'),
								('ir_attachment','ir.attachment'),('mail_message','mail.message'),('mail_tracking_value','mail.tracking.value'),
								('helpdesk_ticket','helpdesk.ticket'),('helpdesk_ticket_team','helpdesk.ticket.team'),('helpdesk_ticket_stage','helpdesk.ticket.stage'),
								('helpdesk_ticket_tag','helpdesk.ticket.tag'),('helpdesk_ticket_category','helpdesk.ticket.category'),('helpdesk_ticket_channel','helpdesk.ticket.channel')],'tablas', default='res_partner')
	archivo_nombre = fields.Char('')
	archivo_contenido = fields.Binary(string="Archivos generados", readonly=True,)
	
	archivo_sql = fields.Binary(string="Archivos generados", readonly=True,)
	archivo_nombre_sql = fields.Char('')

	archivo_para_errores = fields.Char('')
	archivo_errores_contenidos = fields.Binary(string="Error?")
	mostrar = fields.Char('')

	#CREAR FUNCION PARA DESCARGAR MENSAJES, NOTIFICACIONES, CRM, TICKET. 
	
	def export_crm_mensajes(self):
			
		crm_mjes=self.env['mail.message'].search([('model','=','crm.lead')])

		
		#CUDIADO RES_ID, PARENT_ID,CHILD_IDS no es el mismo
		campos_mjes=['id','subject', 'date', 'body', 'attachment_ids', 'parent_id', 'child_ids', 'model', 
						'res_id', 'record_name', 'message_type', 'subtype_id', 'mail_activity_type_id', 
						'email_from', 'author_id', 'author_avatar', 'partner_ids', 'needaction_partner_ids', 
						'needaction', 'channel_ids', 'notification_ids', 'starred_partner_ids', 'starred', 
						'tracking_value_ids', 'no_auto_thread', 'message_id', 'reply_to', 'mail_server_id', 
						'description', 'website_published', 'id', 'display_name', 'create_uid', 'create_date', 
						'write_uid', 'write_date']
		titulos=''

		for i in campos_mjes:
			titulos+=i+'; '
		
		dato=titulos+ '\n'


		ids=[i.id for i in crm_mjes]
		#serializo y me llevo los ids
		self.id_mensajes_crm=json.dumps(ids)



		for rec in crm_mjes:

			sql = '''select name from ir_model_data where model='mail.message' and res_id=%(id)s '''
			self.env.cr.execute(sql, {'id': rec.id})
			id_ext = self.env.cr.fetchall()
			
			id_externo=id_ext[0][0] if id_ext else ''
			
			dato+=id_externo+'; '+ str(rec.subject)+'; '+ str(rec.date) +'; '+ str(rec.body)+'; '+str(rec.attachment_ids)+'; '+str(rec.parent_id.id)+'; '+str(rec.child_ids.ids) +'; '+str(rec.model)+'; '
			dato+=	str(rec.res_id)+'; '+ str(rec.record_name)+'; '+ str(rec.message_type)+'; '+ str(rec.subtype_id.id)+'; '+ str(rec.mail_activity_type_id.id)
			dato+= '; '+str(rec.email_from)+'; '+ str(rec.author_id.id)+'; '+str(rec.author_avatar)+'; '+str(rec.partner_ids.ids)+'; '+str(rec.needaction_partner_ids.ids)
			dato+= '; '+str(rec.needaction)+'; '+str(rec.channel_ids.ids)+'; '+str(rec.notification_ids.ids)+'; '+str(rec.starred_partner_ids.ids)+'; '+str(rec.starred)
			dato+= '; '+str(rec.tracking_value_ids.ids)+'; '+str(rec.no_auto_thread)+'; '+str(rec.message_id)+'; '+str(rec.reply_to)+'; '+str(rec.mail_server_id)
			dato+= '; '+rec.description.replace('\n','')+'; '+str(rec.website_published)+'; '+str(rec.id)+'; '+str(rec.display_name)+'; '+str(rec.create_uid)+'; '+str(rec.create_date)
			dato+= '; '+str(rec.write_uid)+'; '+str(rec.write_date)+'\n'
			
		
				
		self.archivo_nombre='Registro_Mensajes_CRM.CSV'
		data_to_save = codecs.encode(dato, 'utf-8')
		data_to_save = base64.encodestring(data_to_save)
		self.archivo_contenido=data_to_save


	
	def export_crm_tracking(self):

		#crm_model=self.env['crm.lead'].search([('id','=',417)])
		ids=json.loads(self.id_mensajes_crm)
		crm_track=self.env['mail.tracking.value'].search([('mail_message_id','in',ids)])

		
		campos_mjes=['id_mje_ext','field', 'field_desc', 'field_type', 'old_value_integer', 'old_value_float', 'old_value_monetary', 
		'old_value_char', 'old_value_text', 'old_value_datetime', 'new_value_integer', 'new_value_float', 
		'new_value_monetary', 'new_value_char', 'new_value_text', 'new_value_datetime', 'mail_message_id', 
		'id', 'display_name', 'create_uid', 'create_date', 'write_uid', 'write_date']
		titulos=''

		for i in campos_mjes:
			titulos+=i+'; '
		
		dato=titulos+ '\n'


		for rec in crm_track:

			sql = '''select name from ir_model_data where model='mail.message' and res_id=%(id)s '''
			self.env.cr.execute(sql, {'id': rec.mail_message_id.id})
			id_ext = self.env.cr.fetchall()
			
			id_externo=id_ext[0][0] if id_ext else ''

			dato+=id_externo +';'+str(rec.field)+'; '+str(rec.field_desc)+'; '+str(rec.field_type)+'; '+str(rec.old_value_integer)+'; '+str(rec.old_value_float)+'; '+str(rec.old_value_monetary)+';'
			dato+=str(rec.old_value_char)+';'+str(rec.old_value_text)+'; '+str(rec.old_value_datetime)+';'+str(rec.new_value_integer)+';'+str(rec.new_value_float)+';'
			dato+=str(rec.new_value_monetary)+'; '+str(rec.new_value_char)+'; '+str(rec.new_value_text)+'; '+str(rec.new_value_datetime)+'; '+str(rec.mail_message_id)+'; '
			dato+=str(rec.id)+'; '+str(rec.display_name)+'; '+str(rec.create_uid)+'; '+str(rec.create_date)+'; '+str(rec.write_uid)+'; '+str(rec.write_date)+'\n'
		
		

		self.archivo_nombre='Registro_Tracking_CRM.CSV'
		data_to_save = codecs.encode(dato, 'utf-8')
		data_to_save = base64.encodestring(data_to_save)
		self.archivo_contenido=data_to_save





	def export_helpdesk_mensajes(self):
			
		help_mjes=self.env['mail.message'].search([('model','=','helpdesk.ticket')])
				
		#CUDIADO RES_ID, PARENT_ID,CHILD_IDS no es el mismo
		campos_mjes=['id','subject', 'date', 'body', 'attachment_ids', 'parent_id', 'child_ids', 'model', 
						'res_id', 'record_name', 'message_type', 'subtype_id', 'mail_activity_type_id', 
						'email_from', 'author_id', 'author_avatar', 'partner_ids', 'needaction_partner_ids', 
						'needaction', 'channel_ids', 'notification_ids', 'starred_partner_ids', 'starred', 
						'tracking_value_ids', 'no_auto_thread', 'message_id', 'reply_to', 'mail_server_id', 
						'description', 'website_published', 'id', 'display_name', 'create_uid', 'create_date', 
						'write_uid', 'write_date']
		titulos=''

		for i in campos_mjes:
			titulos+=i+'; '
		
		dato=titulos+ '\n'


		ids=[i.id for i in help_mjes]
		#serializo y me llevo los ids
		self.id_mensajes_helpdesk=json.dumps(ids)


		for rec in help_mjes:

			sql = '''select name from ir_model_data where model='mail.message' and res_id=%(id)s '''
			self.env.cr.execute(sql, {'id': rec.id})
			id_ext = self.env.cr.fetchall()
			
			id_externo=id_ext[0][0] if id_ext else ''
			
			dato+=id_externo+'; '+ str(rec.subject)+'; '+ str(rec.date) +'; '+ str(rec.body).replace('\n','')+'; '+str(rec.attachment_ids.id)+'; '+str(rec.parent_id.id)+'; '+str(rec.child_ids.ids) +'; '+str(rec.model)+'; '
			dato+=	str(rec.res_id)+'; '+ str(rec.record_name)+'; '+ str(rec.message_type)+'; '+ str(rec.subtype_id.id)+'; '+ str(rec.mail_activity_type_id.id)
			dato+= '; '+str(rec.email_from)+'; '+ str(rec.author_id.id)+'; '+str(rec.author_avatar)+'; '+str(rec.partner_ids.ids)+'; '+str(rec.needaction_partner_ids.ids)
			dato+= '; '+str(rec.needaction)+'; '+str(rec.channel_ids.ids)+'; '+str(rec.notification_ids.ids)+'; '+str(rec.starred_partner_ids.ids)+'; '+str(rec.starred)
			dato+= '; '+str(rec.tracking_value_ids.ids)+'; '+str(rec.no_auto_thread)+'; '+str(rec.message_id)+'; '+str(rec.reply_to)+'; '+str(rec.mail_server_id)
			dato+= '; '+rec.description.replace('\n','')+'; '+str(rec.website_published)+'; '+str(rec.id)+'; '+str(rec.display_name)+'; '+str(rec.create_uid)+'; '+str(rec.create_date)
			dato+= '; '+str(rec.write_uid)+'; '+str(rec.write_date)+'\n'
			#dato+= ', '+str(rec.write_uid)+', '+str(rec.write_date)+', '+str(rec.__last_update)+'\n'
	
			
		self.archivo_nombre='Registro_Mensajes_HELPDESK-TICKET.CSV'
		data_to_save = codecs.encode(dato, 'utf-8')
		data_to_save = base64.encodestring(data_to_save)
		self.archivo_contenido=data_to_save




	def export_helpdesk_tracking(self):

		#crm_model=self.env['crm.lead'].search([('id','=',417)])
		ids=json.loads(self.id_mensajes_helpdesk)
		help_track=self.env['mail.tracking.value'].search([('mail_message_id','in',ids)])
				
		campos_mjes=['id_mje_ext','field', 'field_desc', 'field_type', 'old_value_integer', 'old_value_float', 'old_value_monetary', 
		'old_value_char', 'old_value_text', 'old_value_datetime', 'new_value_integer', 'new_value_float', 
		'new_value_monetary', 'new_value_char', 'new_value_text', 'new_value_datetime', 'mail_message_id', 
		'id', 'display_name', 'create_uid', 'create_date', 'write_uid', 'write_date']
		titulos=''

		for i in campos_mjes:
			titulos+=i+'; '
		
		dato=titulos+ '\n'


		for rec in help_track:

			sql = '''select name from ir_model_data where model='mail.message' and res_id=%(id)s '''
			self.env.cr.execute(sql, {'id': rec.mail_message_id.id})
			id_ext = self.env.cr.fetchall()
			
			id_externo=id_ext[0][0] if id_ext else ''

			dato+=id_externo +';'+str(rec.field)+'; '+str(rec.field_desc)+'; '+str(rec.field_type)+'; '+str(rec.old_value_integer)+'; '+str(rec.old_value_float)+'; '+str(rec.old_value_monetary)+';'
			dato+=str(rec.old_value_char)+';'+str(rec.old_value_text)+'; '+str(rec.old_value_datetime)+';'+str(rec.new_value_integer)+';'+str(rec.new_value_float)+';'
			dato+=str(rec.new_value_monetary)+'; '+str(rec.new_value_char)+'; '+str(rec.new_value_text)+'; '+str(rec.new_value_datetime)+'; '+str(rec.mail_message_id)+'; '
			dato+=str(rec.id)+'; '+str(rec.display_name)+'; '+str(rec.create_uid)+'; '+str(rec.create_date)+'; '+str(rec.write_uid)+'; '+str(rec.write_date)+'\n'
		
		

		self.archivo_nombre='Registro_Tracking_HELPDESK-TICKET.CSV'
		data_to_save = codecs.encode(dato, 'utf-8')
		data_to_save = base64.encodestring(data_to_save)
		self.archivo_contenido=data_to_save


	def export_sql(self):
		
		columnas=''' SELECT column_name
  					FROM information_schema.columns
 					WHERE table_schema = 'public'
   					AND table_name   = %(tabla)s '''


		self.env.cr.execute(columnas, {'tabla': self.tablas})
		col = self.env.cr.fetchall()
		
		columnas_csv = ''
		for i in col:
			columnas_csv+=str(i[0])+'; '

		columnas_csv+='\n'

		sql = '''select * from ''' + self.tablas
		self.env.cr.execute(sql)
		resultado = self.env.cr.fetchall()
		
		cuerpo_csv=''
		for c in resultado:
			count=0
			for linea in c:
				count+=1

				if self.tablas=='res_users' and (count==7) and linea:
					linea=linea.replace("\n","")

				if self.tablas=='res_partner' and (count==14 or count==30 or count==31) and linea:
					linea=linea.replace("'","").replace("\n","..")
									
				if self.tablas=='crm_lead' and count==10 and linea:
					linea=linea.replace('\n','') 					
				if self.tablas=='crm_lead' and (count==39 or count==38) and linea:
					linea=linea.replace("'","").replace("\n","")
				if self.tablas=='ir_attachment' and (count==21) and linea:
					linea=linea.replace("\n","")
				if self.tablas=='mail_message' and (count==4 or count==12) and linea:
					linea=linea.replace("\n","")
				if self.tablas=='helpdesk_ticket' and (count==4) and linea:
					linea=linea.replace("\n"," ")				
				
				cuerpo_csv+=str(linea)+'; '

			cuerpo_csv+='\n'
			

		csvfile=columnas_csv + cuerpo_csv
		

		self.archivo_nombre_sql='Registro_{}.CSV'.format(self.tablas)
		data_to_save = codecs.encode(csvfile, 'utf-8')
		data_to_save = base64.encodestring(data_to_save)
		self.archivo_sql=data_to_save

	



	def import_mensajes(self):
		self.mostrar=''
		#Decodificación y separación en líneas
		lineas = base64.b64decode(self.file)
		
		lineas= lineas.decode("utf-8")
		lineas = lineas.split('\n')
		
		no_titulo=None
		lineas_archivo=0

		for i in lineas:
						
			lineas_archivo+=1

			#Separando los datos del movimiento
			mov = i.split(';')
			
			campos={}
			res_id = None

			if len(mov)>1 and lineas_archivo>1:
								
				id_externo=mov[0]

				sql = '''select res_id from ir_model_data where name = %(id_ext)s '''
				self.env.cr.execute(sql, {'id_ext': id_externo})
				id_ext = self.env.cr.fetchall()
				res_users= int(''.join([s for s in mov[32] if s.isdigit()]))
				mail_= ''.join([s for s in mov[27].split() if s.isdigit()])
				mail_= int(mail_) if mail_ and mail_!=''  else False 
				
				if id_ext:
					res_id = id_ext[0][0]
					ticket_mjes=self.env['mail.message'].search([('id','=',res_id)])
					
					campos={
					'subject': mov[1][1:] if mov[1][1:] != 'False' and mov[1][1:]!='' else False,
					'date':datetime.strptime(mov[2][1:], '%Y-%m-%d %H:%M:%S') if mov[2] else False,
					'body':mov[3][1:] ,  
					'attachment_ids':[(4,i) for i in eval(mov[4]) if i] if eval(mov[4]) else False,
					'parent_id':eval(mov[5]) if eval(mov[5]) else False,
					'child_ids': [(4,i) for i in eval(mov[6]) if i] if eval(mov[6]) else False,
					'model':mov[7][1:] ,
					'res_id':eval(mov[8]) if eval(mov[8]) else False,
					'record_name':mov[9][1:],
					'message_type':mov[10][1:],
					'subtype_id':eval(mov[11]) if eval(mov[11]) else False,
					'mail_activity_type_id':eval(mov[12]) if eval(mov[12]) else False, 
					'email_from':mov[13][2:],
					'author_id':eval(mov[14]) if eval(mov[14]) else False,
					'author_avatar': eval(mov[15][1:]) if eval(mov[15][1:]) else False,
					'partner_ids':[(4,i) for i in eval(mov[16]) if i] if eval(mov[16]) else False,
					'needaction_partner_ids':[(4,i) for i in eval(mov[17]) if i] if eval(mov[17]) else False,
					'needaction':eval(mov[18]) ,
					'channel_ids':[(4,i) for i in eval(mov[19]) if i] if eval(mov[19]) else False,
					'notification_ids':[(4,i) for i in eval(mov[20]) if i] if eval(mov[20]) else False,
					'starred_partner_ids':[(4,i) for i in eval(mov[21]) if i] if eval(mov[21]) else False,
					'starred':eval(mov[22]) , 
					'tracking_value_ids':[(4,i) for i in eval(mov[23]) if i] if eval(mov[23]) else False,
					'no_auto_thread':eval(mov[24]) ,
					'message_id':mov[25][1:] if mov[25] else False , 
					'reply_to':mov[26][2:],
					'mail_server_id':mail_ if mail_ else False, 
					'description':mov[28][1:],
					'website_published':eval(mov[29]) ,
					'display_name':mov[31][1:],
					'create_uid': res_users if res_users else False,
					'create_date':datetime.strptime(mov[33][1:], '%Y-%m-%d %H:%M:%S') if mov[33] else False, 
					'write_uid':res_users if res_users else False,
					'write_date':datetime.strptime(mov[35][1:], '%Y-%m-%d %H:%M:%S') if mov[35] else False,

						}
					try:
						ticket_mjes.write(campos)
						self.mostrar='Se importaron correctamente los registros de Helpdesk Mensajes'

					except Exception as e:
						self.mostrar='Error en registros de Helpdesk Mensjaes, id_ext: ' + str(res_id) +',res_id: '+str(ticket_mjes.id)
						self.env.cr.rollback()
						raise e



	def import_tracking(self):
		#Decodificación y separación en líneas
		self.mostrar=''
		lineas = base64.b64decode(self.file)
		
		lineas= lineas.decode("utf-8")
		lineas = lineas.split('\n')
		
		no_titulo=None
		lineas_archivo=0

		
		for i in lineas:
						
			lineas_archivo+=1

			# Separando los datos del movimiento
			mov = i.split(';')
			
			campos={}
			res_id = None

			if len(mov)>1 and lineas_archivo>1:
									
				id_externo=mov[0]
				sql = '''select res_id from ir_model_data where name = %(id_ext)s '''
				self.env.cr.execute(sql, {'id_ext': id_externo})
				id_ext = self.env.cr.fetchall()
				#print(id_ext)
				res_users= int(''.join([s for s in mov[19] if s.isdigit()]))
				mail_= int(''.join([s for s in mov[16] if s.isdigit()]))

				#['mail_message_4417_250918d3', 'planned_revenue', ' \ufeffIngreso estimado', ' float', ' 0', ' 88888.0', ' 0.0',
				#'False', 'False', ' False', '0', '99999.0', '0.0', ' False', ' False', ' False', ' mail.message(4417,)', 
				#' 10', ' planned_revenue', ' res.users(1,)', ' 2020-06-03 04:02:52', ' res.users(1,)', ' 2020-06-03 04:02:52']

													
				if id_ext:
					res_id = id_ext[0][0]
					crm_mjes_track=self.env['mail.tracking.value'].search([('mail_message_id','=',res_id)])
					campos={
						'field':mov[1][1:],
						'field_desc':mov[2][1:],
						'field_type':mov[3][1:] if mov[3] else False ,
						'old_value_integer':eval(mov[4]) if eval(mov[4]) else False ,
						'old_value_float':mov[5] if eval(mov[5]) else False ,
						'old_value_monetary':eval(mov[6]) if eval(mov[6]) else False ,
						'old_value_char':mov[7] if mov[7] and mov[7] != 'False' else False ,
						'old_value_text':mov[8] if mov[8] and mov[8] != 'False'  else False ,
						'old_value_datetime':datetime.strptime(mov[9][1:], '%Y-%m-%d %H:%M:%S') if eval(mov[9]) else False,
						'new_value_integer':eval(mov[10]) if eval(mov[10]) else False ,
						'new_value_float':eval(mov[11]) if eval(mov[11]) else False ,
						'new_value_monetary':eval(mov[12]) if eval(mov[12]) else False ,
						'new_value_char':mov[13][1:] if mov[13][1:] and mov[13][1:] != 'False' else False ,
						'new_value_text':mov[14][1:] if mov[14][1:] and mov[14][1:] != 'False' else False ,
						'new_value_datetime':datetime.strptime(mov[15][1:], '%Y-%m-%d %H:%M:%S') if eval(mov[15]) else False,
						'mail_message_id':mail_ if mail_ else False ,
						'display_name':mov[18][1:],
						'create_uid':res_users,
						'create_date':datetime.strptime(mov[20][1:], '%Y-%m-%d %H:%M:%S') if mov[20] else False,
						'write_uid':res_users,
						'write_date':datetime.strptime(mov[22][1:], '%Y-%m-%d %H:%M:%S') if mov[22] else False,
 						}
					
					try:
						crm_mjes_track.write(campos)
						self.mostrar='Se importaron correctamente los registros de Helpdesk tracking'
						

					except Exception as e:
						self.mostrar='Error en registros de helpdesk tracking, id_ext' + str(res_id) +'res_id'+str(eval(mov[17]))
						print('Error en resgistro ','Id_ext',res_id,'res_id',eval(mov[17]))
						self.env.cr.rollback()
						raise e

