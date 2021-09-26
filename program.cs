// From https://www.thingiverse.com/thing:2358314/files CC-ND
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;

using System.Threading.Tasks;
using System.Globalization;

/*
 *  Step #1, shift all X to {parameter one} as origin
 *  Step #2, shift all Y to {parameter two} as origin
 *  Step #3, add forward offset to X value
 *  Step #4, adjust Z value to correct for hyp
 * 
 */

namespace GCodeShifter
{

    class Program
    {

        static double Angle = 35.0;
        static double Hyp = 0.0;
        static double Adj = 0.0;

        static double x_original = 0;
        static double y_original = 0;
        static double x_offset;
        static double currentOffset = 0.0;

        static void Main(string[] args)
        {

            string inputFile = args[0];
            string outputFile = args[1];
            string xoffsetLength = "";
            string yoffsetLength = "";
            string newAngle = "";


            // if we have an Y offset, record it
            if (args.Length > 2)
            {
                xoffsetLength = args[2];
                Double.TryParse(xoffsetLength, out x_original);
            };

            // if we have a Y offset, record it
            if (args.Length > 3)
            {
                yoffsetLength = args[3];
                Double.TryParse(yoffsetLength, out y_original);
            }

            // if we have a angle, record it
            if (args.Length > 4)
            {
                string newHyp = args[4];
                Double.TryParse(newHyp, out Hyp);
            }

            // if we have a angle, record it
            if (args.Length > 5)
            {
                string newAdj = args[5];
                Double.TryParse(newAdj, out Adj);
            }

            // calculate triangle sides
            //Hyp = 1 / System.Math.Cos(Angle);
            //Adj = System.Math.Tan(Angle);

            try
            {

                using (StreamReader sr = File.OpenText(inputFile))
                {
                    using (StreamWriter sw = new StreamWriter(outputFile))
                    {
                        string s = String.Empty;
                        while ((s = sr.ReadLine()) != null)
                        {
                            sw.WriteLine(ProcessLine(s.TrimStart(), sw));
                        }
                    }
                }
            }

            catch (Exception ex)
            {
                Console.WriteLine(ex.Message.ToString());
            }
            // close files
            Console.WriteLine("GCodeShifter Complete");

            //}
        }

        static string ProcessLine(string lineData, StreamWriter sw)
        {
            string[] temp;
            temp = lineData.Split(Char.Parse(" "));

            StringBuilder tempData = new StringBuilder(temp.Length);

            // if the first parameter is a G0 with a trailing Z
            // then this is a Z height change
            // we need to multiply the layer height by the Square Root of Two
            // and record the layer height, as it will be the offset going forward
            if (temp[0] == "G0" && (lineData.IndexOf("Z") > 0))
            {

                double currentZ = double.Parse(lineData.Substring(lineData.IndexOf("Z") + 1, (lineData.Length - lineData.IndexOf("Z") - 1)));

                if (currentOffset == 0.0)
                {
                    // capture the very first layer height (as this is the X offset going forward.)
                    currentOffset = currentZ * Adj;  // .7 is the adjacent side length of a 35 degree angle
                }

                // then read the offset value to shift the layer
                currentZ = currentZ * Hyp;

                lineData = lineData.Substring(0, lineData.IndexOf("Z") + 1) + currentZ.ToString();
                temp = lineData.Split(Char.Parse(" "));

                // and remember to add the new X offset
                x_offset = x_offset + currentOffset;

            }


            if (currentOffset != 0.0)
            {

                // if we are on a G0 or G1 line (no Z!)
                if ((temp[0] == "G0" || temp[0] == "G1"))
                {
                    if (lineData.IndexOf("X") > 0)
                    {
                        if (lineData.IndexOf("Y") > 0)
                        {
                            bool xFixed = false;
                            bool yFixed = false;

                            for (int segment = 0; segment < temp.Length; segment++)
                            {
                                if (temp[segment].StartsWith("X") && !xFixed)
                                {
                                    double xValue = double.Parse(temp[segment].Substring(1));
                                    temp[segment] = "X" + (xValue + x_offset + x_original).ToString();
                                    xFixed = !xFixed;
                                }

                                if (temp[segment].StartsWith("Y") && !yFixed)
                                {
                                    double yValue = double.Parse(temp[segment].Substring(1));
                                    temp[segment] = "Y" + (yValue + y_original).ToString();
                                    yFixed = !yFixed;
                                }
                            }

                            lineData = "";
                            foreach (string segment in temp)
                            {
                                lineData = lineData + segment + " ";
                            }

                        }
                    }
                }
            }
            return lineData;
        }
    }
}
