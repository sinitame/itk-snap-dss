import requests, os, time


main_url="http://itk.10.7.11.23.nip.io"
service_hash="6e8775d466d865ce30eab35aa6d9a871a5d39816"
provider="IBM-LAB"

while True:
    claim_api_url = "{0}/api/pro/services/claims".format(main_url)

    claim_response = requests.post(claim_api_url, data={"services":service_hash,"provider":provider,"code":"01"})
    claim_response_content = claim_response.content.decode('utf-8')

    if claim_response_content=='None':
        time.sleep(10)
    else:
        ticket_id = claim_response_content.split(",")[0]

        ticket_directory = "/service/data/ticket{0}".format(ticket_id)
        os.makedirs(ticket_directory, exist_ok=True)

        list_file_api_url = "{0}/api/pro/tickets/{1}/files/input".format(main_url,ticket_id)

        files_to_download = requests.get(list_file_api_url)

        for row in files_to_download.text.split('\n')[:-1]:
            file_id = row.split(',')[0]
            file_name = row.split(',')[1][:-1]
            file_url = "{0}/api/pro/tickets/{1}/files/input/{2}".format(main_url, ticket_id, file_id)    
            download = requests.get(file_url)
            file_path = ticket_directory + "/" + file_name
            open(file_path, 'wb').write(download.content)

            print("Downloaded ", file_path)
