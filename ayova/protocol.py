"""E2E encryption protocol using NaCl (Curve25519 XSalsa20 Poly1305)"""
import json
import base64
from datetime import datetime
from typing import Optional, Dict, Tuple
import nacl.public
import nacl.encoding
import nacl.utils


class Protocol:
    """NaCl Box E2E encryption - encrypt with recipient's public key"""
    
    @staticmethod
    def encrypt_message(plaintext: str, sender_private_key: bytes, 
                       recipient_public_key: bytes) -> Dict:
        """Encrypt message for recipient using NaCl Box"""
        # Load keys
        sender_sk = nacl.public.PrivateKey(sender_private_key)
        recipient_pk = nacl.public.PublicKey(recipient_public_key)
        
        # Create ephemeral keypair for this message (Perfect Forward Secrecy)
        ephemeral_sk = nacl.public.PrivateKey.generate()
        
        # Encrypt using Box (Curve25519 XSalsa20 Poly1305)
        box = nacl.public.Box(ephemeral_sk, recipient_pk)
        nonce = nacl.utils.random(nacl.public.Box.NONCE_SIZE)
        encrypted = box.encrypt(plaintext.encode(), nonce)
        
        # Sign the encrypted message with sender's identity key
        # (separate from the box keys)
        
        return {
            'ciphertext': base64.b64encode(encrypted).decode(),
            'ephemeral_pubkey': base64.b64encode(bytes(ephemeral_sk.public_key)).decode(),
            'sender_pubkey': base64.b64encode(bytes(sender_sk.public_key)).decode(),
            'timestamp': datetime.utcnow().isoformat(),
            'version': 'ayova-e2e-v1'
        }
    
    @staticmethod
    def decrypt_message(envelope: Dict, recipient_private_key: bytes) -> Optional[str]:
        """Decrypt message with recipient's private key"""
        try:
            # Load keys
            recipient_sk = nacl.public.PrivateKey(recipient_private_key)
            ephemeral_pk = nacl.public.PublicKey(
                base64.b64decode(envelope['ephemeral_pubkey'])
            )
            
            # Decrypt using Box
            box = nacl.public.Box(recipient_sk, ephemeral_pk)
            ciphertext = base64.b64decode(envelope['ciphertext'])
            plaintext = box.decrypt(ciphertext)
            
            return plaintext.decode()
        except Exception:
            return None
    
    @staticmethod
    def create_secure_payload(message: str, sender_signing_key, 
                            recipient_public_key: bytes) -> bytes:
        """Create complete encrypted payload for network transport"""
        # For P2P, we need sender's encryption key (derived from signing key)
        # In practice, Ed25519 keys can be converted to Curve25519
        from nacl.bindings import crypto_sign_ed25519_pk_to_curve25519
        from nacl.bindings import crypto_sign_ed25519_sk_to_curve25519
        
        # Convert Ed25519 keys to Curve25519 for Box encryption
        sender_curve_sk = crypto_sign_ed25519_sk_to_curve25519(bytes(sender_signing_key))
        recipient_curve_pk = crypto_sign_ed25519_pk_to_curve25519(recipient_public_key)
        
        envelope = Protocol.encrypt_message(message, sender_curve_sk, recipient_curve_pk)
        
        # Add signature with Ed25519 for authentication
        message_bytes = json.dumps(envelope, sort_keys=True).encode()
        signature = sender_signing_key.sign(message_bytes).signature
        
        payload = {
            'envelope': envelope,
            'signature': base64.b64encode(signature).decode()
        }
        
        return json.dumps(payload).encode()
    
    @staticmethod
    def verify_and_decrypt(payload: bytes, recipient_signing_key,
                          sender_public_key: bytes) -> Optional[str]:
        """Verify signature and decrypt message"""
        try:
            data = json.loads(payload)
            envelope = data['envelope']
            signature = base64.b64decode(data['signature'])
            
            # Verify signature
            message_bytes = json.dumps(envelope, sort_keys=True).encode()
            try:
                sender_vk = nacl.signing.VerifyKey(sender_public_key)
                sender_vk.verify(message_bytes, signature)
            except Exception:
                return None  # Signature invalid
            
            # Decrypt
            from nacl.bindings import crypto_sign_ed25519_sk_to_curve25519
            recipient_curve_sk = crypto_sign_ed25519_sk_to_curve25519(
                bytes(recipient_signing_key)
            )
            
            return Protocol.decrypt_message(envelope, recipient_curve_sk)
        except Exception:
            return None


def pack_message(message: str, sender_signing_key, recipient_pubkey: bytes) -> bytes:
    """High-level message packing"""
    return Protocol.create_secure_payload(message, sender_signing_key, recipient_pubkey)


def unpack_message(payload: bytes, recipient_signing_key, sender_pubkey: bytes) -> Optional[str]:
    """High-level message unpacking"""
    return Protocol.verify_and_decrypt(payload, recipient_signing_key, sender_pubkey)
