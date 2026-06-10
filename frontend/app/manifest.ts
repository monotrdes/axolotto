import { MetadataRoute } from 'next';

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'Axolotto',
    short_name: 'Axolotto',
    description: 'La lotería del futuro con Axolotitos NFT en la blockchain.',
    start_url: '/play',
    display: 'standalone',
    background_color: '#0a0a0f',
    theme_color: '#E4007C',
    orientation: 'portrait',
    icons: [
      {
        src: '/icon.svg',
        sizes: 'any',
        type: 'image/svg+xml',
        purpose: 'any',
      },
      {
        src: '/icon.svg',
        sizes: 'any',
        type: 'image/svg+xml',
        purpose: 'maskable',
      },
    ],
  };
}
