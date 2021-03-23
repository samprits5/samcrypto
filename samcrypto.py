'''
Author : Samprit
Date   : 23/03/2021
'''
import os
import re
import sys
from cryptography.fernet import Fernet
from multiprocessing.dummy import Pool as ThreadPool

DEFAULT_SECRET_KEY_PATH  = r'your_secret_key_path\samcrypto.key'
THREAD_BATCH_SIZE        = 10

def help():
	"""
	Shows the usage of the script
	"""
	print("\nSamcrypto - Symmetric Encryption Tool (AES-128-CBC)")
	print("\nUsage : samcrypto -[OPTION] *[VALUE]")
	print("\nExamples :")
	print("Key Generate : samcrypto -g C:\\Users\\USER\\Desktop")
	print("Encryption   : samcrypto -k samcrypto.key -e file.txt")
	print("Decryption   : samcrypto -k samcrypto.key -d file.txt.samcrypto")


def collect_files(source, file_type=''):
	try:
		if not os.path.isdir(source):
			return False, "Message : Invalid path provided"
		print("\nCollecting the files...")
		all_files = []
		for root, dirs, files in os.walk(source):
			for file in files:
				relativePath = os.path.relpath(root, source)
				if relativePath == ".":
					relativePath = ""
				if re.search(fr"{file_type}$", file, re.IGNORECASE):
					all_files.append(os.path.join(
						source, os.path.join(relativePath, file)))

		print("Found", len(all_files), "file(s)")
		return True, all_files
	except Exception as e:
		return False, "Message : Problem in collecting files"

def key_generate(source=os.getcwd()):
	"""
	Generates a key and save it into samcrypto.key file
	"""
	try:
		if not os.path.isdir(source):
			return False, "Message : Invalid path provided"

		key = Fernet.generate_key()

		keypath = os.path.join(source, 'samcrypto.key')

		with open(keypath, 'wb') as filekey: 
			filekey.write(key)

		return True, "Message : Encryption key generated successfully!"

	except Exception as e:
		return False, str(e)

def read_key(keypath=''):
	"""
	Reads a key from file and returns byte value
	"""
	try:
		if not os.path.isfile(keypath):
			return False, "Message : Invalid encryption key path"

		with open(keypath, 'rb') as filekey: 
			key = filekey.read()
		return key, "Message : Success"
	except Exception as e:
		return False, str(e)

def encrypt_file(key=None, file=''):
	"""
	Encrypts a file with Secret Key
	"""
	try:
		if (key is None) or (not isinstance(key, (bytes, bytearray))):
			return False, "Message : Invalid encryption key!"

		if not os.path.isfile(file):
			return False, "Message : Invalid source file!"

		fernet = Fernet(key) 
	
		# opening the original file to encrypt 
		with open(file, 'rb') as f: 
			original = f.read() 
		
		# encrypting the file 
		encrypted = fernet.encrypt(original)

		head, tail = os.path.split(file)

		output_filepath = os.path.join(head, tail + ".samcrypto")
		  
		# opening the file in write mode and  
		# writing the encrypted data
		with open(output_filepath, 'wb') as encrypted_file: 
			encrypted_file.write(encrypted)

		return True, "Message : {} encrypted successfully!".format(tail)

	except Exception as e:
		return False, str(e)


def decrypt_file(key=None, file=''):
	"""
	Decrypts a file with Secret Key
	"""
	try:
		if (key is None) or (not isinstance(key, (bytes, bytearray))):
			return False, "Message : Invalid encryption key!"

		if not os.path.isfile(file):
			return False, "Message : Invalid source file!"

		fernet = Fernet(key)

		# opening the encrypted file to decrypt 
		with open(file, 'rb') as f: 
			encrypted_data = f.read()

		# decrypting the file 
		decrypted_data = fernet.decrypt(encrypted_data) 

		head, tail = os.path.split(file)

		if ".samcrypto" in tail:
			tail = tail.replace(".samcrypto", "")

		output_filepath = os.path.join(head, tail)

		# opening the file in write mode and 
		# writing the decrypted data 
		with open(output_filepath, 'wb') as dec_file: 
			dec_file.write(decrypted_data) 

		return True, "Message : {} decrypted successfully!".format(tail)

	except Exception as e:
		return False, str(e)

def main():

	args = sys.argv

	if '-h' in args:
		help()
		return

	if '-g' in args:
		# Finding Key Store Path
		index = args.index('-g')
		try:
			value = args[index+1]
		except IndexError:
			value = None

		if value is None:
			key, msg = key_generate()
		else:
			key, msg = key_generate(source=value)

		print("\n" + msg)

		return

	if '-e' in args:
		# Finding Encryption Key
		if not '-k' in args:
			key=None
		else:
			index_key = args.index('-k')
			try:
				key = args[index_key+1]
				if key == 'D':
					key = DEFAULT_SECRET_KEY_PATH
			except Exception as e:
				key=None

		# Finding Encryption Values
		index = args.index('-e')
		try:
			file = args[index+1]
		except IndexError:
			file = ''

		# Encryption Starts
		key, msg = read_key(key)

		key, msg = encrypt_file(key=key, file=file)

		print("\n" + msg)

		return

	if '-d' in args:
		# Finding Decryption Key
		if not '-k' in args:
			key=None
		else:
			index_key = args.index('-k')
			try:
				key = args[index_key+1]
				if key == 'D':
					key = DEFAULT_SECRET_KEY_PATH
			except Exception as e:
				key=None

		# Finding Decryption Values
		index = args.index('-d')
		try:
			file = args[index+1]
		except IndexError:
			file = ''

		# Decryption Starts
		key, msg = read_key(key)

		key, msg = decrypt_file(key=key, file=file)

		print("\n" + msg)

		return

	if '-E' in args:
		# Finding Encryption Key
		if not '-k' in args:
			key=None
		else:
			index_key = args.index('-k')
			try:
				key = args[index_key+1]
				if key == 'D':
					key = DEFAULT_SECRET_KEY_PATH
			except Exception as e:
				key=None

		# Finding Encryption Values
		index = args.index('-E')
		try:
			dirs = args[index+1]
		except IndexError:
			dirs = ''

		# Collecting the Files
		status, files = collect_files(dirs)
		if not status:
			print("\n" + files)
			return

		# Encryption Starts
		key, _ = read_key(key)

		pool = ThreadPool(THREAD_BATCH_SIZE)

		results = pool.starmap(encrypt_file, zip([key for _ in range(len(files))], files))

		pool.close()
		pool.join()

		# Printing results of the threads
		print('\n', end='')
		for msg_obj in results:
			print(msg_obj[-1])

		return

	if '-D' in args:
		# Finding Decryption Key
		if not '-k' in args:
			key=None
		else:
			index_key = args.index('-k')
			try:
				key = args[index_key+1]
				if key == 'D':
					key = DEFAULT_SECRET_KEY_PATH
			except Exception as e:
				key=None

		# Finding Decryption Values
		index = args.index('-D')
		try:
			dirs = args[index+1]
		except IndexError:
			dirs = ''

		# Collecting the Files
		status, files = collect_files(dirs, file_type='.samcrypto')
		if not status:
			print("\n" + files)
			return

		# Decryption Starts
		key, _ = read_key(key)

		pool = ThreadPool(THREAD_BATCH_SIZE)

		results = pool.starmap(decrypt_file, zip([key for _ in range(len(files))], files))

		pool.close()
		pool.join()

		# Printing results of the threads
		print('\n', end='')
		for msg_obj in results:
			print(msg_obj[-1])

		return

if __name__ == '__main__':
	main()