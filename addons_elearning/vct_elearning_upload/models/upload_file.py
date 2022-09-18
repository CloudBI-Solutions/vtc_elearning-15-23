import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
# bucket name va region name các bạn set up trong env cho tiện nha
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
REGION_NAME = os.getenv("REGION_NAME")

# connect tới s3 thông qua boto3, ở đây thì key và secret key chúng ta đã set up bằng aws cli rồi nên không cần nữa nha
s3 = boto3.client('s3')

from odoo import api, fields, models

class SlideSlide(models.Model):
    _inherit = 'slide.slide'


    file_slide = fields.Binary(string='File slide')
    test = fields.Char('URL')
    bucket_name = fields.Char('bucket_name')

    def get_url_attachment(self, attachment_id):
        attachment = self.env['ir.attachment'].sudo().browse(attachment_id)
        return "web/content2/?model=ir.attachment&id=" + str(
            attachment_id) + "&filename_field=name&field=datas&download=true&name=" + attachment.name

    # Hàm này kiểm tra xem 1 bucket nào đó đã tồn tại chưa, ví dụ như bạn muốn kiểm tra trước khi tạo chẳng hạn
    def check_bucket_exist(self, bucket_name="slide"):
        try:
            response = s3.list_buckets()
            buckets = [bucket['Name'] for bucket in response['Buckets']]
            return bucket_name in buckets
        except Exception as e:
            return False

    # Hàm này để tạo 1 bucket mới
    def create_new_bucket(self, bucket_name="slide"):
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
                'LocationConstraint': REGION_NAME
            }
        )

    # file_path ở đây là đường dẫn và file mà bạn muốn upload lên.
    # Ví dụ bạn chỉ muốn upload file logo.png ở ngay thư mục ngoài của bucket thì file_path="logo.png", còn nếu bạn muốn chứa file upload lên trong một thư mục nữa thì file_path="framgia/logo.png".
    # Lúc này nếu folder framgia chưa có trên bucket thì nó sẽ tự tạo cho bạn luôn (len3)
    def upload_file_to_s3(self, file, file_path, bucket_name=S3_BUCKET_NAME, acl="public-read"):
        S3_LOCATION = "http://{}.s3.amazonaws.com/{}".format(S3_BUCKET_NAME, file_path)
        try:
            data = s3.upload_fileobj(
                file,
                bucket_name,
                file_path,
                ExtraArgs={
                    "ACL": acl,
                    "ContentType": file.content_type
                }
            )
            return S3_LOCATION
        except Exception as e:
            return e

    # Hàm này để get file nha
    def get_file_from_s3(self, file_path, bucket_name=S3_BUCKET_NAME):
        # Đoạn này mình kiểm tra luôn nếu mà cái bucket_name không tồn tại thì thôi khỏi get file mất công
        if not self.check_bucket_exist(bucket_name):
            return None
        try:
            # generate_presigned_url chỉ là một trong những cách bạn có thể tương tác với file trên s3, ở đây mình muốn lấy url của 1 file lưu private trên s3, ví dụ như cần lấy ảnh bằng link chẳng hạn
            url = s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': file_path
                },
                ExpiresIn=3600)
            self.test = url
            return url
        except Exception as e:
            return e

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    public_url = fields.Char('Public Image', compute='get_url_attachment', help='This is the link for the image or file')

    # def _create_url(self):
    #     for record in self:
    #         base_url = self.env['ir.config_parameter'].get_param('web.base.url')
    #         record.public_url = base_url + '/web/content/' + str(record.id) + str(record.name)

    def get_url_attachment(self):
        for record in self:
            attachment = self.env['ir.attachment'].sudo().browse(record.id)
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            record.public_url = base_url + "web/content2/?model=ir.attachment&id=" + str(
                record.id) + "&filename_field=name&field=datas&download=true&name=" + attachment.name