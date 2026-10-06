scp -r outputs/site/. "${AGH_LOGIN}@${AGH_HOST}:public_html/${AGH_FOLDER}/"
ssh "${AGH_LOGIN}@${AGH_HOST}" "find public_html/${AGH_FOLDER} -type d -exec chmod 755 {} + && find public_html/${AGH_FOLDER} -type f -exec chmod 644 {} +"
