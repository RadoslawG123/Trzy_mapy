AGH_FOLDER="landsat-$(date +%Y%m%d-%H%M%S)"
ssh "${AGH_LOGIN}@${AGH_HOST}" "mkdir -p public_html/${AGH_FOLDER} && chmod 755 public_html public_html/${AGH_FOLDER}"
