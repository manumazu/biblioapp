from flask import Flask, render_template, request, abort, flash, redirect, json, escape, session, url_for, jsonify, \
Response, send_from_directory
import flask_login, os, glob, time, datetime
from PIL import Image
from werkzeug.utils import secure_filename
            

'''
Static pages
'''
def set_routes_for_static_pages(app):

  @app.route("/")
  def root():
    #detect language in header request
    browserLang = request.accept_languages.best_match(app.available_locales)
    language = app.default_language
    if browserLang is not None:
      language = browserLang.split('_')[0]
    return redirect(url_for('presentation', language=language, _scheme='https', _external=True))

  @app.route("/<language>")
  def presentation(language = 'fr'):
    userName = ""
    if flask_login.current_user.is_authenticated:
      userName=flask_login.current_user.name
    if language not in app.languages:
      language = 'fr'
    #print(app.languages[language]) 
    return render_template('index.html', **app.languages[language], current_language=language, available_languages=app.available_languages, user_login=userName)

  @app.route('/privacy')
  def privacy():
	  return render_template('privacy.html') 

  @app.route('/offline')
  def offline():
	  return render_template('offline.html')       

  @app.route('/apple-app-site-association')
  @app.route('/manifest.json')
  @app.route('/favicon.ico')
  @app.route('/sw.js')
  def static_from_root():
	  return send_from_directory(app.static_folder, request.path[1:])

  @app.route('/.well-known/assetlinks.json')
  def assetlinks():
    return send_from_directory(app.static_folder, 'assetlinks.json') 

  @app.route('/olivier', methods=['GET', 'POST'])
  def diapo_olivier():
    if request.method == 'POST':
        if 'file1' not in request.files:
            flash('Veuillez sélectionner un dossier')
            return redirect(request.url)
        file1 = request.files['file1']
        desc = request.form['description']          
        if file1.filename == '':
            flash('Aucun fichier sélectionné', 'warning')
            return redirect(request.url)
        if desc == '':
            flash('Ajouter une description', 'warning')
            return redirect(request.url)            
        if file1 and allowed_file(file1.filename):
            filename = secure_filename(file1.filename)
            upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER']) 
            count_img = os.listdir(upload_dir+'/photos')
            nb_img = len(count_img)
            filename =  str(nb_img) + '_' + filename
            #save image 
            full_path_img = os.path.join(upload_dir, 'photos', filename)
            file1.save(full_path_img)
            
            #resize image
            img = Image.open(full_path_img)
            width, height = img.size
            ratio = width/height
            img_resized = img.resize((900,int(900/ratio))) if(ratio > 1) else img.resize((600,int(600/ratio)))
            img_resized_path = os.path.join(upload_dir, 'photos', 'resize', filename)
            img_resized.save(img_resized_path)
            
            #save descrition
            descFile = open(os.path.join(upload_dir, filename+'.txt'), 'w')
            descFile.writelines(desc)
            descFile.close()
            #render partial album
            relative_img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'photos', 'resize', filename)
            rendered = render_template('diaporamaOliv_partial.html', path = relative_img_path, description = desc)
            #generate full album
            msg = refresh_diapo_olivier()
            print(msg)
            return rendered
        flash('Format de fichier non autorisé', 'warning')
        return redirect(request.url)
    return render_template('oliv_form.html')

  @app.route('/olivier-refresh', methods=['GET'])
  def refresh_diapo_olivier():
    #generate full album 
    upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    files_list = glob.glob(upload_dir+'/*.txt')
    album_array = []
    # retrieve info
    for file_name in files_list:
      file_path = os.path.join(upload_dir, file_name)
      with open(file_path, 'r') as f:
        img_desc = f.readlines()
        f.close()
      modified = os.path.getmtime(file_path)
      year,month,day,hour,minute,second=time.gmtime(modified)[:-3]
      img_date = "%02d/%02d/%d %02d:%02d:%02d"%(day,month,year,hour,minute,second)
      #print(img_date)
      img_path = file_name.replace('.txt','')
      img_path = img_path.replace(upload_dir, '../images/photos/resize')
      img_name = img_path.replace('../images/photos/resize/', '')
      # check ratio for forcing height
      img = Image.open(os.path.join(upload_dir,'photos','resize',img_name))
      width, height = img.size
      ratio = width/height
      force_height = False if ratio > 1 else True  
      # store infos in array
      img_infos = {'description':img_desc, 'path':img_path, 'filename':img_name, 'date':img_date, 'force_height':force_height}
      album_array.append(img_infos)
    print(album_array)
    #save html render in album file
    render_album = render_template('diaporamaOliv.html', imageInfos = album_array)
    pathHTML = os.path.join(upload_dir, 'full_album.html')
    fileHTML = open(pathHTML, "w")
    fileHTML.writelines(render_album)
    fileHTML.close()
    return f"{len(files_list)} slides generated"

  def allowed_file(filename):
    return '.' in filename and \
      filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

