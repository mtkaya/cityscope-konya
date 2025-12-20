export default {
    plugins: {
        '@tailwindcss/postcss': {},
        autoprefixer: {}, // autoprefixer is recommended but v4 includes it? Docs say to use @tailwindcss/postcss which handles it. 
        // actually v4 docs say just @tailwindcss/postcss is enough, but including autoprefixer is harmless or good.
        // Let's stick to v4 minimal:
    },
}
