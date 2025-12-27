from django.db.models.signals import pre_save,post_delete
from django.dispatch import receiver
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

from report.models import AssignedTask,AssignedLetter
from .models import Violation, StoredGoodImage
import os
from django.core.files.storage import default_storage
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from .models import DernewNetijesi


def delete_old_care_nus_file(instance):
    """Deletes the old file if a new one is uploaded."""
    if not instance.pk:  # If it's a new instance, do nothing
        return  

    try:
        old_instance = AssignedLetter.objects.get(pk=instance.pk)
    except AssignedLetter.DoesNotExist:
        return  # Old instance doesn't exist, no file to delete

    if old_instance.care_nusga and old_instance.care_nusga != instance.care_nusga:
        old_file_path = old_instance.care_nusga.path
        if os.path.isfile(old_file_path):  # Ensure file exists before deleting
            os.remove(old_file_path)

@receiver(pre_save, sender=AssignedLetter)
def pre_save_delete_old_care_nusga_file(sender, instance, **kwargs):
    """Deletes old file before updating the object."""
    delete_old_care_nus_file(instance)  # Delete old file immediately

@receiver(post_delete, sender=AssignedLetter)
def post_delete_remove_care_nusga_file(sender, instance, **kwargs):
    """Deletes the file when the object is deleted."""
    if instance.care_nusga:
        file_path = instance.care_nusga.path
        if os.path.isfile(file_path):  # Ensure file exists before deleting
            os.remove(file_path)

def delete_old_bilermen_nus_file(instance):
    """Deletes the old file if a new one is uploaded."""
    if not instance.pk:  # If it's a new instance, do nothing
        return  

    try:
        old_instance = AssignedTask.objects.get(pk=instance.pk)
    except AssignedTask.DoesNotExist:
        return  # Old instance doesn't exist, no file to delete

    if old_instance.bilermen_nusga and old_instance.bilermen_nusga != instance.bilermen_nusga:
        old_file_path = old_instance.bilermen_nusga.path
        if os.path.isfile(old_file_path):  # Ensure file exists before deleting
            os.remove(old_file_path)

@receiver(pre_save, sender=AssignedTask)
def pre_save_delete_old_bilermen_nusga_file(sender, instance, **kwargs):
    """Deletes old file before updating the object."""
    delete_old_bilermen_nus_file(instance)  # Delete old file immediately

@receiver(post_delete, sender=AssignedTask)
def post_delete_remove_bilermen_nusga_file(sender, instance, **kwargs):
    """Deletes the file when the object is deleted."""
    if instance.bilermen_nusga:
        file_path = instance.bilermen_nusga.path
        if os.path.isfile(file_path):  # Ensure file exists before deleting
            os.remove(file_path)

def delete_old_dernew_netije_file(instance):
    """Deletes the old file if a new one is uploaded."""
    if not instance.pk:  # If it's a new instance, do nothing
        return  

    try:
        old_instance = DernewNetijesi.objects.get(pk=instance.pk)
    except DernewNetijesi.DoesNotExist:
        return  # Old instance doesn't exist, no file to delete

    if old_instance.hatyn_nusgasy and old_instance.hatyn_nusgasy != instance.hatyn_nusgasy:
        old_file_path = old_instance.hatyn_nusgasy.path
        if os.path.isfile(old_file_path):  # Ensure file exists before deleting
            os.remove(old_file_path)

@receiver(pre_save, sender=DernewNetijesi)
def pre_save_delete_old_dernew_netije_file(sender, instance, **kwargs):
    """Deletes old file before updating the object."""
    delete_old_dernew_netije_file(instance)  # Delete old file immediately

@receiver(post_delete, sender=DernewNetijesi)
def post_delete_remove_dernew_netije_file(sender, instance, **kwargs):
    """Deletes the file when the object is deleted."""
    if instance.hatyn_nusgasy:
        file_path = instance.hatyn_nusgasy.path
        if os.path.isfile(file_path):  # Ensure file exists before deleting
            os.remove(file_path)

@receiver(pre_save, sender=Violation)
def reset_fields_on_violation_type_change(sender, instance, **kwargs):
    # Check if the instance already exists (update scenario)
    if instance.pk:
        # Retrieve the original instance from the database
        original = Violation.objects.get(pk=instance.pk)

        # If the violation_type has changed
        if original.violation_type != instance.violation_type:
            # If changing to 'individual' or 'official', reset fields related to 'legal entity'
            if original.violation_type == 'legal entity' or instance.violation_type in ['individual', 'official']:
                instance.company_name = None
                instance.address = None
                instance.phone = None

            # If changing to 'legal entity', reset fields specific to 'individual' and 'official'
            elif instance.violation_type == 'legal entity':
                instance.violator_name = None
                instance.violator_surname = None
                instance.father_name = None
                instance.date_of_birth = None
                instance.place_of_birth = None
                instance.passport_number = None
                instance.passport_issue_date = None
                instance.nationality = None
                instance.violator_address = None


@receiver(pre_save, sender=StoredGoodImage)
def resize_image(sender, instance, **kwargs):
    """
    Signal to resize images before saving them to the StoredGoodImage model.
    """
    # Check if there's an image in the instance
    if not instance.image:
        return

    try:
        # Open the image
        img = Image.open(instance.image)

        # Define maximum dimensions for the image
        max_width, max_height = 800, 800

        # Resize the image if it exceeds the maximum dimensions
        if img.width > max_width or img.height > max_height:
            # Use thumbnail to keep aspect ratio without distortion
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        # Convert the image to RGB if it's in another mode (e.g., PNG with alpha channel)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Save the image to a BytesIO object
        output = BytesIO()
        img.save(output, format='JPEG', quality=70, optimize=True, progressive=True)
        output.seek(0)

        # Generate a unique name for the new image to avoid conflicts
        new_filename = f"{os.path.splitext(instance.image.name)[0]}_resized.jpg"

        # Replace the image field with the resized image
        instance.image = InMemoryUploadedFile(
            output,
            'ImageField',
            new_filename,
            'image/jpeg',
            output.getbuffer().nbytes,
            None
        )

    except Exception as e:
        # Log the error for debugging (You can also use Django's logging framework)
        print(f"Error resizing image: {e}")

@receiver(pre_save, sender=StoredGoodImage)
def delete_old_image_on_update(sender, instance, **kwargs):
    """
    Signal to delete old image from the storage when the StoredGoodImage
    model is updated with a new image.
    """
    if not instance.pk:
        # If there's no primary key, it's a new instance, so no old image to delete
        return

    try:
        # Fetch the current/old image from the database
        old_image = sender.objects.get(pk=instance.pk).image

        # Check if there's a new image set for this instance and it's different from the old one
        if old_image and old_image.url != instance.image.url:
            # Delete the old image file from storage
            if default_storage.exists(old_image.name):
                default_storage.delete(old_image.name)

    except sender.DoesNotExist:
        # The instance is new, so there's no old image to delete
        pass


@receiver(post_delete, sender=StoredGoodImage)
def delete_image_on_instance_delete(sender, instance, **kwargs):
    """
    Signal to delete the image from the storage when the StoredGoodImage
    model instance is deleted.
    """
    # Delete the image file from storage when the instance is deleted
    if instance.image and default_storage.exists(instance.image.name):
        default_storage.delete(instance.image.name)