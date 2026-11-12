using System;
using System.IO;
using AssetRipper.Assets;
using AssetRipper.Assets.Process;
using AssetRipper.Assets.Process.Unit;

namespace StarmakerExtractor
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Starmaker Asset Extractor");
            Console.WriteLine("Starting extraction...");
            
            // Path to Starmaker Story Data
            string starmakerPath = "/home/jesusgs/proyectos/starmaker/game/Starmaker 1.8E/Starmaker Story_Data/";
            string outputPath = "/home/jesusgs/proyectos/starmaker/extracted_assets/";
            
            // Create output directory if it doesn't exist
            if (!Directory.Exists(outputPath))
            {
                Directory.CreateDirectory(outputPath);
                Console.WriteLine($"Created output directory: {outputPath}");
            }
            
            // Process all .asset files in Starmaker Story Data
            string[] assetFiles = Directory.GetFiles(starmakerPath, "*.asset", SearchOption.AllDirectories);
            
            Console.WriteLine($"Found {assetFiles.Length} asset files to process.");
            
            foreach (string assetFile in assetFiles)
            {
                try
                {
                    Console.WriteLine($"Processing: {assetFile}");
                    
                    // Load the asset bundle
                    var assetProcessor = new AssetProcessor();
                    var unitProcessor = new UnitProcessor();
                    
                    // Load the asset
                    var assetBundle = assetProcessor.LoadAsset(assetFile);
                    
                    // Process the asset
                    unitProcessor.ProcessAsset(assetBundle, outputPath);
                    
                    Console.WriteLine($"Successfully processed: {assetFile}");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error processing {assetFile}: {ex.Message}");
                }
            }
            
            Console.WriteLine("Extraction completed!");
        }
    }
}