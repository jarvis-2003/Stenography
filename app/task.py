from celery import current_app  as celery
from PIL import Image
import io

@celery.task
def process_image(file_data,text):
    # Your existing code
    if isinstance(file_data, str):  # Handle file path
        with open(file_data, "rb") as f:
            file_data = f.read()
    elif not isinstance(file_data, bytes):  # Raise error if not binary
        raise ValueError("Expected image file as binary data")
    
    image = Image.open(io.BytesIO(file_data))  # Assuming image_file is binary data from the request
    image = image.convert('RGB')
    width, height = image.size

    # Extract the pixels from the image
    pixels = []
    for y in range(height):
        for x in range(width):
            r, g, b = image.getpixel((x, y))
            pixels.append((r, g, b))

    # Preprocess the text (convert to binary)
    text = text.strip()
    count = 0
    temp = []
    secret = []

    for c in text:
        # Convert character to its 8-bit binary form
        binary = format(ord(c), '08b')

        if count < 3:
            temp.append(binary)
            count += 1

        if count == 3:
            # When count reaches 3, create a tuple and append to secret
            tup = tuple(temp)
            secret.append(tup)
            count = 0
            temp = []

    # If there are any remaining binary strings in 'temp', add them as the last tuple
    if temp:
        # Pad the last tuple with '00000000' if it has fewer than 3 elements
        while len(temp) < 3:
            temp.append('00000000')
        tup = tuple(temp)
        secret.append(tup)

    # Now we embed the binary data into the image pixels
    new_tup = []
    for x in range(len(secret)):
        if pixels[x][0] > 200 and pixels[x][1] > 200 and pixels[x][2] > 200:
            key = x
            while key < len(pixels):
                if pixels[key][0] < 200 or pixels[key][1] < 200 or pixels[key][2] < 200:
                    break
                else:
                    key += 1

            # now we have got a key that is no white
            index = 0
            for element in secret[x]:
                res = xor_and_complement(element, format(pixels[key][index], '08b'))
                new_tup.append(int(res, 2))
                index += 1
            pixels[key] = tuple(new_tup)
            key = 0
            new_tup = []
        else:
            index = 0
            for element in secret[x]:
                res = xor_and_complement(element, format(pixels[x][index], '08b'))
                new_tup.append(int(res, 2))
                index += 1
            pixels[x] = tuple(new_tup)

            new_tup = []

    # Create a new image with the modified pixels
    image = Image.new('RGB', (width, height))
    image.putdata(pixels)

# Save the modified image to a BytesIO object in PNG format (lossless)
    image_io = io.BytesIO()
    image.save(image_io, format='PNG')  # Save as PNG for lossless quality
    image_io.seek(0)

    # Return the image as a response with PNG mimetype
    return image_io.getvalue()


def xor_and_complement(bin1, bin2):
    # Ensure the strings are of equal length (8 bits in this case)
    max_len = max(len(bin1), len(bin2))
    bin1 = bin1.zfill(max_len)
    bin2 = bin2.zfill(max_len)

    # Perform XOR operation
    xor_result = int(bin1, 2) ^ int(bin2, 2)
    xor_binary = bin(xor_result)[2:].zfill(max_len)  # Convert back to binary string

    # Compute the complement (flip bits)
    complement = ''.join(('1' if bit == '0' else '0') for bit in xor_binary)

    return complement




# here it goes the logic for reverse image processing.

@celery.task

def reverse_image(image_og,output_image):
    if isinstance(output_image, str):  # Handle file path
        with open(output_image, "rb") as g:
            output_image = g.read()
    elif not isinstance(output_image, bytes):  # Raise error if not binary
        raise ValueError("Expected image file as binary data")
    try:
        image = Image.open(io.BytesIO(output_image))
        image = image.convert('RGB')
        width, height = image.size
    except Exception as e:
        raise ValueError(f"Failed to process output image: {e}")
    

    image_with_secret = []
    image_original = []

    for y in range(height):
        for x in range(width):
            r, g, b = image.getpixel((x, y))
            image_with_secret.append((r, g, b))


    if isinstance(image_og, str):  # Handle file path
        with open(image_og, "rb") as m:
            image_og = m.read()
    elif not isinstance(image_og, bytes):  # Raise error if not binary
        raise ValueError("Expected image file as binary data")
    
    try:
        og_image = Image.open(io.BytesIO(image_og))
        og_image = og_image.convert('RGB')
        wid, hei = og_image.size
    except Exception as e:
        raise ValueError(f"Failed to process original image: {e}")
    
    for y in range(hei):
        for x in range(wid):
            r, g, b = og_image.getpixel((x, y))
            image_original.append((r, g, b))

    result_code = reversesecurity(secret_dict(image_with_secret, image_original), image_original)

    converted_chars = []
    for tup in result_code:
        # Convert each value in the tuple to a character
        char = ''.join(chr(x) for x in tup if x != 0)  # Ignore 0 since it's typically a padding value
        converted_chars.append(char)

    # Join the converted characters into a single string
    result_string = ''.join(converted_chars)
    print(result_string)
    return result_string

def secret_dict(image_with_secret, image_original):
    secret_dict = {}
    for x in range(len(image_with_secret)):
        if image_with_secret[x] != image_original[x]:
            secret_dict[x] = image_with_secret[x]  # Use x as the key and the tuple as the value
        else:
            continue
    return secret_dict


def reversesecurity(secret_dict, image_original):
    updated_dict = {}
    final_code = []
    for (key, value) in secret_dict.items():
        new_tup = []
        for x in value:
            x_binary = bin(x)[2:].zfill(8)
            complement = ''.join('1' if bit == '0' else '0' for bit in x_binary)
            new_tup.append(int(complement, 2))
        updated_dict[key] = tuple(new_tup)

    for key, value in updated_dict.items():
        new_tup = []
        index = 0
        for x in value:
            res = x ^ image_original[key][index]
            new_tup.append(res)
            index += 1
        final_code.append(tuple(new_tup))
    return final_code
