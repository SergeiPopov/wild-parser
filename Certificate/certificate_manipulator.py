import re
import logging
from datetime import datetime

import SQL


class CertManipulator:
    def __init__(self, lite_connector: SQL.LiteConnector):
        self.lite_connector = lite_connector

    @staticmethod
    def get_value_by_keys(fsa_cert_dict, *args):
        for target_keys in args:
            full_target_keys_flag = True
            temp_var = fsa_cert_dict.copy()
            for key in target_keys.split('|'):
                if isinstance(temp_var, dict) and key in temp_var.keys():
                    temp_var = temp_var[key]
                    continue
                full_target_keys_flag = False
                break

            if full_target_keys_flag:
                return temp_var

        return str(None)

    @staticmethod
    def get_contacts_from_cert(fsa_cert):
        contacts = CertManipulator.get_value_by_keys(fsa_cert, 'applicant|contacts')
        org_email = 'None '
        org_mobile_number = 'None  тел.'
        org_home_number = 'None '
        if contacts is not str(None):
            for contact in contacts:
                if re.search(r'@', contact.get('value')):
                    org_email += ' ' + contact.get('value')
                elif re.search(r'(\+7|\b89)', contact.get('value')):
                    org_mobile_number += ' ' + contact.get('value')
                else:
                    org_home_number += ' ' + contact.get('value')
        org_email = org_email.replace('None  ', '').strip()
        org_mobile_number = org_mobile_number.replace('None  ', '').strip()
        org_home_number = org_home_number.replace('None  ', '').strip()
        return org_email, org_mobile_number, org_home_number

    @staticmethod
    def get_address(fsa_cert):
        org_address = CertManipulator.get_value_by_keys(fsa_cert, 'applicant|addresses',
                                                        'applicant|regOrganName')

        if isinstance(org_address, list) and len(org_address):
            org_address = org_address[0].get('fullAddress')
        else:
            org_address = CertManipulator.get_value_by_keys(fsa_cert, 'applicant|regOrganName', 'manufacturer|regOrganName')
        return str(org_address)

    def check_cert_by_id(self, cert_id):
        check_prod_sql = f"""SELECT * from certificate WHERE certificate_id = {cert_id}"""
        self.lite_connector.cursor.execute(check_prod_sql)
        return True if self.lite_connector.cursor.fetchone() else False

    def insert_cert_from_parser(self, fsa_cert, card_id, certificate_url):
        certificate_id = CertManipulator.get_value_by_keys(fsa_cert, 'idCertificate', 'idDeclaration')
        if self.check_cert_by_id(certificate_id):
            logging.info(f"Сертификат с номером {certificate_id} уже записан в базу")
            return False
        certificate_number = CertManipulator.get_value_by_keys(fsa_cert, 'number')
        certRegDate = CertManipulator.get_value_by_keys(fsa_cert, 'certRegDate', 'declRegDate')
        certEndDate = CertManipulator.get_value_by_keys(fsa_cert, 'certEndDate', 'declEndDate')

        surname = CertManipulator.get_value_by_keys(fsa_cert, 'applicant|surname')
        firstname = CertManipulator.get_value_by_keys(fsa_cert, 'applicant|firstName')
        patronymic = CertManipulator.get_value_by_keys(fsa_cert, 'applicant|patronymic')
        FIO = str(surname) + " " + str(firstname) + " " + str(patronymic)

        org_name = CertManipulator.get_value_by_keys(fsa_cert, 'applicant|fullName', 'applicant|shortName')
        org_email, org_mobile_number, org_home_number = CertManipulator.get_contacts_from_cert(fsa_cert)
        org_address = CertManipulator.get_address(fsa_cert)
        parse_data = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        insert_prod_sql = f"""INSERT INTO certificate(certificate_id, certificate_url, certificate_number, certRegDate, certEndDate, FIO, org_name, org_email, org_mobile_number, org_other_contact, org_address, parse_date, card_id) 
                                                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        params = (certificate_id,
                  certificate_url,
                  certificate_number,
                  certRegDate,
                  certEndDate,
                  FIO,
                  org_name,
                  org_email,
                  org_mobile_number,
                  org_home_number,
                  org_address,
                  parse_data,
                  card_id
                  )
        self.lite_connector.cursor.execute(insert_prod_sql, params)
        self.lite_connector.commit()
        logging.info(f"Сертификат {certificate_number} был записан в базу данных")
        return True
